-- 520 Quest payments: support for the Lemon Squeezy webhook (supabase/functions/lemon-webhook).
-- Paste into Supabase > SQL Editor and click Run, after 001_core.sql. Safe to run again.

-- Every webhook event we have acted on. The key makes retries harmless; the time keeps an old event from undoing a newer one.
create table if not exists public.payment_events (
  event_key text primary key,
  event_name text not null,
  subscription_id text,
  event_time timestamptz not null,
  email text,
  user_id uuid,
  plan text not null check (plan in ('free', 'monthly', 'sixmonth', 'yearly')),
  test_mode boolean not null default false,
  outcome text not null default 'processing',
  received_at timestamptz not null default now()
);
create index if not exists payment_events_subscription on public.payment_events (subscription_id, event_time desc);

-- Someone paid with an email that has no account yet. The plan is applied when that account is created.
create table if not exists public.pending_plans (
  email text primary key,
  plan text not null check (plan in ('free', 'monthly', 'sixmonth', 'yearly')),
  event_time timestamptz not null,
  test_mode boolean not null default false,
  created_at timestamptz not null default now()
);

alter table public.payment_events enable row level security; -- no policies: only the service role (the webhook) can touch these
alter table public.pending_plans enable row level security;
revoke all on public.payment_events, public.pending_plans from anon, authenticated;

-- The one place a plan changes. Returns: applied, pending, duplicate, stale or unmatched.
create or replace function public.apply_payment(
  p_event_key text, p_event_name text, p_user uuid, p_email text, p_plan text,
  p_event_time timestamptz, p_subscription text, p_test boolean
) returns text
language plpgsql security definer set search_path = public as $$
declare
  v_id uuid;
  v_email text := nullif(lower(btrim(coalesce(p_email, ''))), '');
  v_outcome text;
begin
  if p_plan not in ('free', 'monthly', 'sixmonth', 'yearly') then raise exception 'bad plan %', p_plan; end if;

  insert into payment_events (event_key, event_name, subscription_id, event_time, email, plan, test_mode)
  values (p_event_key, p_event_name, p_subscription, p_event_time, v_email, p_plan, coalesce(p_test, false))
  on conflict (event_key) do nothing;
  if not found then return 'duplicate'; end if;

  if p_subscription is not null and exists (
    select 1 from payment_events
    where subscription_id = p_subscription and event_time > p_event_time
      and event_key <> p_event_key and outcome in ('applied', 'pending')
  ) then
    update payment_events set outcome = 'stale' where event_key = p_event_key;
    return 'stale';
  end if;

  select id into v_id from profiles where id = p_user;
  if v_id is null and v_email is not null then
    select id into v_id from profiles where lower(email) = v_email limit 1;
  end if;

  if v_id is not null then
    update profiles set
      plan = p_plan,
      plan_since = case when p_plan = 'free' then null when plan = 'free' or plan_since is null then now() else plan_since end
    where id = v_id;
    if v_email is not null then delete from pending_plans where email = v_email; end if;
    v_outcome := 'applied';
  elsif v_email is not null then
    insert into pending_plans (email, plan, event_time, test_mode)
    values (v_email, p_plan, p_event_time, coalesce(p_test, false))
    on conflict (email) do update set plan = excluded.plan, event_time = excluded.event_time, test_mode = excluded.test_mode
      where pending_plans.event_time <= excluded.event_time;
    v_outcome := 'pending';
  else
    v_outcome := 'unmatched';
  end if;

  update payment_events set outcome = v_outcome, user_id = v_id where event_key = p_event_key;
  return v_outcome;
end $$;
revoke execute on function public.apply_payment(text, text, uuid, text, text, timestamptz, text, boolean) from public, anon, authenticated;
grant execute on function public.apply_payment(text, text, uuid, text, text, timestamptz, text, boolean) to service_role;

-- When an account is created with an email that already paid, apply the plan straight away.
create or replace function public.claim_pending_plan() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record;
begin
  select * into p from pending_plans where email = lower(new.email);
  if found then
    update profiles set plan = p.plan, plan_since = case when p.plan = 'free' then null else now() end where id = new.id;
    delete from pending_plans where email = p.email;
  end if;
  return new;
end $$;
drop trigger if exists claim_pending_plan on public.profiles;
create trigger claim_pending_plan after insert on public.profiles for each row execute function public.claim_pending_plan();
