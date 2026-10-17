-- 520 Quest core schema: accounts, progress sync, devices, plans, paid content, duels, admin alerts.
-- Paste into Supabase > SQL Editor and click Run. Safe to run again.
create extension if not exists pgcrypto with schema extensions;

-- ---------- profiles: one row per account ----------
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  name text,
  plan text not null default 'free' check (plan in ('free', 'pro', 'monthly', 'sixmonth', 'yearly', 'lifetime')),
  plan_since timestamptz,
  level int not null default 1,
  acc int not null default 0,
  created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;
drop policy if exists "read own profile" on public.profiles;
create policy "read own profile" on public.profiles for select to authenticated using (id = auth.uid());
-- Users may change only their display name, level and accuracy; plan changes go through redeem_code or the payment webhook.
drop policy if exists "update own profile" on public.profiles;
create policy "update own profile" on public.profiles for update to authenticated using (id = auth.uid()) with check (id = auth.uid());
revoke update on public.profiles from authenticated, anon;
grant select on public.profiles to authenticated;
grant update (name, level, acc) on public.profiles to authenticated;

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, name) values (new.id, new.email, 'Player' || lpad((floor(random() * 10000))::int::text, 4, '0'))
  on conflict (id) do nothing;
  return new;
end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute function public.handle_new_user();

create or replace function public.is_paid(uid uuid default auth.uid()) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where id = uid and plan <> 'free');
$$;
create or replace function public.has_full_access(uid uuid default auth.uid()) returns boolean
language sql stable security definer set search_path = public as $$
  -- Yearly and Lifetime get every sheet and mnemonic; $39 launch buyers ('pro') are upgraded to Lifetime.
  select exists (select 1 from public.profiles where id = uid and plan in ('yearly', 'lifetime', 'pro'));
$$;

-- ---------- progress: the app's saved state, synced after every question ----------
create table if not exists public.progress (
  user_id uuid primary key references auth.users (id) on delete cascade default auth.uid(),
  state jsonb not null,
  total int not null default 0,
  updated_at timestamptz not null default now()
);
alter table public.progress enable row level security;
drop policy if exists "own progress" on public.progress;
create policy "own progress" on public.progress for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update on public.progress to authenticated;

-- ---------- devices: 3 per paid account, 1 per free account, expire after 90 days unused ----------
create table if not exists public.devices (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade default auth.uid(),
  device_id text not null,
  label text,
  kind text check (kind in ('mobile', 'tablet', 'desktop')),
  last_seen timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (user_id, device_id)
);
alter table public.devices enable row level security;
drop policy if exists "read own devices" on public.devices;
create policy "read own devices" on public.devices for select to authenticated using (user_id = auth.uid());
drop policy if exists "remove own devices" on public.devices;
create policy "remove own devices" on public.devices for delete to authenticated using (user_id = auth.uid());
grant select, delete on public.devices to authenticated;

create or replace function public.register_device(p_device_id text, p_label text, p_kind text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare uid uuid := auth.uid(); lim int; n int;
begin
  if uid is null then raise exception 'sign in first'; end if;
  delete from devices where user_id = uid and last_seen < now() - interval '90 days';
  update devices set last_seen = now(), label = coalesce(p_label, label) where user_id = uid and device_id = p_device_id;
  if found then return jsonb_build_object('ok', true); end if;
  lim := case when is_paid(uid) then 3 else 1 end;
  select count(*) into n from devices where user_id = uid;
  if n >= lim then
    return jsonb_build_object('ok', false, 'limit', lim);
  end if;
  insert into devices (user_id, device_id, label, kind) values (uid, p_device_id, left(p_label, 80), case when p_kind in ('mobile', 'tablet', 'desktop') then p_kind else 'desktop' end);
  return jsonb_build_object('ok', true);
end $$;
grant execute on function public.register_device(text, text, text) to authenticated;

-- ---------- unlock codes: only hashes are stored; redeeming upgrades the account ----------
create table if not exists public.unlock_codes (
  code_hash text primary key,
  plan text not null default 'pro'
);
alter table public.unlock_codes enable row level security; -- no policies: never readable from the app
insert into public.unlock_codes (code_hash, plan) values ('dc0b3e3e3aed783131957d2c79b7dca52954b12d15d657aca671d57ee3078658', 'pro') on conflict do nothing;

create or replace function public.redeem_code(p_code text) returns jsonb
language plpgsql security definer set search_path = public, extensions as $$
declare uid uuid := auth.uid(); p text;
begin
  if uid is null then raise exception 'sign in first'; end if;
  select plan into p from unlock_codes where code_hash = encode(digest(upper(trim(p_code)), 'sha256'), 'hex');
  if p is null then return jsonb_build_object('ok', false); end if;
  update profiles set plan = case when plan in ('lifetime', 'yearly') then plan else p end, plan_since = coalesce(plan_since, now()) where id = uid;
  return jsonb_build_object('ok', true, 'plan', (select plan from profiles where id = uid));
end $$;
grant execute on function public.redeem_code(text) to authenticated;

-- ---------- paid content: locked sheets and mnemonics ship encrypted; this key unlocks them ----------
create table if not exists public.content_keys (
  id text primary key,
  k text not null
);
alter table public.content_keys enable row level security; -- no policies: read only through get_content_key()
create or replace function public.get_content_key() returns text
language plpgsql stable security definer set search_path = public as $$
begin
  if not has_full_access(auth.uid()) then return null; end if;
  return (select k from content_keys where id = 'v1');
end $$;
grant execute on function public.get_content_key() to authenticated;
-- The key itself is inserted by the setup file you were given, not stored in the code repository.

-- ---------- duels ----------
create table if not exists public.duels (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  status text not null default 'waiting' check (status in ('waiting', 'active', 'completed', 'expired')),
  mode text not null default 'friend' check (mode in ('friend', 'random')),
  player1_id uuid not null references auth.users (id) on delete cascade,
  player2_id uuid references auth.users (id) on delete cascade,
  player1_name text,
  player2_name text,
  player1_level int,
  player1_acc int,
  questions text[] not null,
  player1_answers jsonb,
  player2_answers jsonb,
  player1_score int,
  player2_score int,
  player1_time int,
  player2_time int,
  winner_id uuid,
  category text not null default 'ALL',
  invite_code text unique
);
create index if not exists duels_invite_code_idx on public.duels (invite_code);
create index if not exists duels_open_random_idx on public.duels (mode, status, created_at) where player2_id is null;
alter table public.duels enable row level security;
-- No direct reads: the functions below return duels with the opponent's answers hidden until you've played.
drop policy if exists "players read own duels" on public.duels;
revoke all on public.duels from anon, authenticated;

create or replace function public.mask_duel(d public.duels, uid uuid) returns public.duels
language plpgsql immutable as $$
begin
  if d.status <> 'completed' then
    if uid = d.player1_id and d.player1_score is null or uid <> d.player1_id then d.player1_answers := null; end if;
    if uid = d.player2_id and d.player2_score is null or uid <> d.player2_id then d.player2_answers := null; end if;
    if uid = d.player1_id and d.player1_score is null then d.player2_score := null; d.player2_time := null; end if;
    if uid = d.player2_id and d.player2_score is null then d.player1_score := null; d.player1_time := null; end if;
  end if;
  return d;
end $$;

create or replace function public.duel_quota_ok(uid uuid, p_category text) returns boolean
language plpgsql stable security definer set search_path = public as $$
begin
  if is_paid(uid) then return true; end if;
  if p_category <> 'BB' then return false; end if;
  return (select count(*) from duels where (player1_id = uid or player2_id = uid) and created_at > date_trunc('day', now())) < 3;
end $$;

-- Settle a duel: winner when both played, or auto-win after 24 hours for the player who did.
create or replace function public.settle_duel(d public.duels) returns void
language plpgsql security definer set search_path = public as $$
begin
  if d.status in ('completed', 'expired') then return; end if;
  if d.player1_score is not null and d.player2_score is not null then
    update duels set status = 'completed', winner_id = case
      when d.player1_score > d.player2_score then d.player1_id
      when d.player2_score > d.player1_score then d.player2_id
      when coalesce(d.player1_time, 0) < coalesce(d.player2_time, 0) then d.player1_id
      when coalesce(d.player2_time, 0) < coalesce(d.player1_time, 0) then d.player2_id
      else null end where id = d.id;
  elsif d.created_at < now() - interval '24 hours' then
    update duels set status = case when d.player1_score is null and d.player2_score is null then 'expired' else 'completed' end,
      winner_id = case when d.player1_score is not null then d.player1_id when d.player2_score is not null then d.player2_id end
      where id = d.id;
  end if;
end $$;

create or replace function public.my_duels() returns setof public.duels
language plpgsql security definer set search_path = public as $$
declare d duels; uid uuid := auth.uid();
begin
  if uid is null then raise exception 'sign in first'; end if;
  for d in select * from duels where uid in (player1_id, player2_id) and status in ('waiting', 'active') loop
    perform settle_duel(d);
  end loop;
  return query select (mask_duel(x, uid)).* from duels x where uid in (x.player1_id, x.player2_id) order by x.created_at desc limit 30;
end $$;
grant execute on function public.my_duels() to authenticated;

create or replace function public.create_duel(p_questions text[], p_category text, p_opponent uuid default null)
returns public.duels language plpgsql security definer set search_path = public as $$
declare uid uuid := auth.uid(); code text; d duels; me profiles;
begin
  if uid is null then raise exception 'sign in first'; end if;
  if array_length(p_questions, 1) <> 10 then raise exception 'a duel needs 10 questions'; end if;
  if not duel_quota_ok(uid, p_category) then raise exception 'duel limit'; end if;
  select * into me from profiles where id = uid;
  loop
    code := 'DUEL-' || lpad((floor(random() * 10000))::int::text, 4, '0');
    exit when not exists (select 1 from duels where invite_code = code and created_at > now() - interval '2 days');
  end loop;
  update duels set invite_code = null where invite_code = code;
  insert into duels (mode, player1_id, player1_name, player1_level, player1_acc, player2_id, questions, category, invite_code, status)
  values ('friend', uid, me.name, me.level, me.acc, p_opponent, p_questions, p_category, code, 'waiting')
  returning * into d;
  return mask_duel(d, uid);
end $$;
grant execute on function public.create_duel(text[], text, uuid) to authenticated;

create or replace function public.join_duel(p_code text) returns public.duels
language plpgsql security definer set search_path = public as $$
declare uid uuid := auth.uid(); d duels;
begin
  if uid is null then raise exception 'sign in first'; end if;
  select * into d from duels where invite_code = upper(trim(p_code)) order by created_at desc limit 1;
  if d.id is null then raise exception 'duel not found'; end if;
  if d.player1_id = uid then return mask_duel(d, uid); end if;
  if d.player2_id = uid then
    update duels set status = 'active' where id = d.id and status = 'waiting' returning * into d;
    select * into d from duels where id = d.id;
    return mask_duel(d, uid);
  end if;
  if d.player2_id is not null then raise exception 'duel already taken'; end if;
  if d.status <> 'waiting' or d.created_at < now() - interval '24 hours' then raise exception 'duel expired'; end if;
  if not duel_quota_ok(uid, d.category) then raise exception 'duel limit'; end if;
  update duels set player2_id = uid, player2_name = (select name from profiles where id = uid), status = 'active' where id = d.id returning * into d;
  return mask_duel(d, uid);
end $$;
grant execute on function public.join_duel(text) to authenticated;

-- Random match: join an open duel within 1 level or 15 accuracy points, else open a new one.
create or replace function public.duel_random(p_questions text[], p_category text) returns public.duels
language plpgsql security definer set search_path = public as $$
declare uid uuid := auth.uid(); d duels; me profiles;
begin
  if uid is null then raise exception 'sign in first'; end if;
  if not duel_quota_ok(uid, p_category) then raise exception 'duel limit'; end if;
  select * into me from profiles where id = uid;
  select * into d from duels
   where mode = 'random' and status = 'waiting' and player2_id is null and player1_id <> uid and category = p_category
     and created_at > now() - interval '24 hours'
     and (abs(coalesce(player1_level, 1) - me.level) <= 1 or abs(coalesce(player1_acc, 0) - me.acc) <= 15)
   order by created_at limit 1 for update skip locked;
  if d.id is not null then
    update duels set player2_id = uid, player2_name = me.name, status = 'active' where id = d.id returning * into d;
    return mask_duel(d, uid);
  end if;
  insert into duels (mode, player1_id, player1_name, player1_level, player1_acc, questions, category, status)
  values ('random', uid, me.name, me.level, me.acc, p_questions, p_category, 'waiting') returning * into d;
  return mask_duel(d, uid);
end $$;
grant execute on function public.duel_random(text[], text) to authenticated;

create or replace function public.submit_duel(p_id uuid, p_answers jsonb, p_score int, p_time int) returns public.duels
language plpgsql security definer set search_path = public as $$
declare uid uuid := auth.uid(); d duels;
begin
  select * into d from duels where id = p_id for update;
  if d.id is null or uid not in (d.player1_id, coalesce(d.player2_id, d.player1_id)) then raise exception 'not your duel'; end if;
  if p_score < 0 or p_score > 10 then raise exception 'bad score'; end if;
  if uid = d.player1_id and d.player1_score is null then
    update duels set player1_answers = p_answers, player1_score = p_score, player1_time = p_time where id = p_id;
  elsif uid = d.player2_id and d.player2_score is null then
    update duels set player2_answers = p_answers, player2_score = p_score, player2_time = p_time where id = p_id;
  end if;
  select * into d from duels where id = p_id;
  perform settle_duel(d);
  select * into d from duels where id = p_id;
  return mask_duel(d, uid);
end $$;
grant execute on function public.submit_duel(uuid, jsonb, int, int) to authenticated;

-- ---------- admin alert: tell the owner when paid accounts pass 400 ----------
create table if not exists public.admin_alerts (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  message text not null
);
alter table public.admin_alerts enable row level security; -- owner reads it in the Table Editor
create or replace function public.check_paid_count() returns trigger
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if new.plan <> 'free' and (old.plan is null or old.plan = 'free') then
    select count(*) into n from profiles where plan <> 'free';
    if n >= 400 and not exists (select 1 from admin_alerts where message like '400 paid%') then
      insert into admin_alerts (message) values ('400 paid accounts reached (' || n || '). Time to move to a paid Supabase plan.');
    end if;
  end if;
  return new;
end $$;
drop trigger if exists paid_count_alert on public.profiles;
create trigger paid_count_alert after update of plan on public.profiles for each row execute function public.check_paid_count();

-- ---------- shared mnemonic upvotes ----------
create table if not exists public.mnemonic_votes (
  user_id uuid not null references auth.users (id) on delete cascade default auth.uid(),
  mn_id text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, mn_id)
);
alter table public.mnemonic_votes enable row level security;
drop policy if exists "read own votes" on public.mnemonic_votes;
create policy "read own votes" on public.mnemonic_votes for select to authenticated using (user_id = auth.uid());
drop policy if exists "add own votes" on public.mnemonic_votes;
create policy "add own votes" on public.mnemonic_votes for insert to authenticated with check (user_id = auth.uid());
drop policy if exists "remove own votes" on public.mnemonic_votes;
create policy "remove own votes" on public.mnemonic_votes for delete to authenticated using (user_id = auth.uid());
revoke all on public.mnemonic_votes from anon, authenticated;
grant select, insert, delete on public.mnemonic_votes to authenticated;
create or replace function public.mnemonic_vote_counts() returns table (mn_id text, n bigint)
language sql stable security definer set search_path = public as $$
  select mn_id, count(*) from mnemonic_votes group by mn_id;
$$;

-- ---------- lock down: the app may call only the functions meant for it ----------
revoke all on public.unlock_codes, public.content_keys, public.admin_alerts from anon, authenticated;
revoke insert, delete, truncate, references, trigger on public.profiles from anon, authenticated;
revoke all on public.profiles, public.progress, public.devices from anon;
revoke insert, update, truncate, references, trigger on public.devices from authenticated;
revoke delete, truncate, references, trigger on public.progress from authenticated;
revoke execute on function public.handle_new_user(), public.check_paid_count(), public.is_paid(uuid), public.has_full_access(uuid),
  public.mask_duel(public.duels, uuid), public.duel_quota_ok(uuid, text), public.settle_duel(public.duels)
  from public, anon, authenticated;
revoke execute on function public.register_device(text, text, text), public.redeem_code(text), public.get_content_key(), public.my_duels(),
  public.create_duel(text[], text, uuid), public.join_duel(text), public.duel_random(text[], text), public.submit_duel(uuid, jsonb, int, int)
  from public, anon;
grant execute on function public.register_device(text, text, text), public.redeem_code(text), public.get_content_key(), public.my_duels(),
  public.create_duel(text[], text, uuid), public.join_duel(text), public.duel_random(text[], text), public.submit_duel(uuid, jsonb, int, int),
  public.mnemonic_vote_counts() to authenticated;
revoke execute on function public.mnemonic_vote_counts() from public;
grant execute on function public.mnemonic_vote_counts() to anon, authenticated;
