-- 520 Quest question reports: students flag a problem with a question from inside the app; the owner sees a fix list.
-- Paste into Supabase > SQL Editor (dropdown next to Save = "Primary database") and click Run, after 001-004. Safe to run again.
--
-- Privacy: no user ids or emails are stored, only a random device id (made in the browser), the question id,
-- a reason and the student's note. One open report per device per question, and at most 30 reports per device per day.

create table if not exists public.q_reports (
  id bigserial primary key,
  qid text not null,
  dev text not null,
  reason text not null,
  note text not null default '',
  status text not null default 'open',          -- open | fixed | dismissed
  created_at timestamptz not null default now()
);
create index if not exists q_reports_status on public.q_reports (status, created_at desc);
create unique index if not exists q_reports_one_open on public.q_reports (dev, qid) where status = 'open';
alter table public.q_reports enable row level security;
revoke all on public.q_reports from public, anon, authenticated; -- read and write only through the functions below

-- Anyone (signed in or not) can send a report. Returns true if it was saved.
create or replace function public.report_question(p_dev text, p_qid text, p_reason text, p_note text) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  if p_dev is null or p_dev !~ '^[A-Za-z0-9-]{8,64}$' or p_qid is null or p_qid !~ '^[A-Za-z0-9_.-]{1,64}$'
     or p_reason is null or p_reason not in ('key', 'typo', 'unclear', 'fact', 'figure', 'other') then return false; end if;
  if (select count(*) from q_reports where dev = p_dev and created_at > now() - interval '1 day') >= 30 then return false; end if;
  insert into q_reports (qid, dev, reason, note) values (p_qid, p_dev, p_reason, left(coalesce(p_note, ''), 1000))
    on conflict (dev, qid) where status = 'open' do update set reason = excluded.reason, note = excluded.note, created_at = now();
  return true;
end $$;

-- Admin only: reports with one status, newest first, as [[id, qid, reason, note, created_at], ...].
create or replace function public.question_reports_admin(p_status text default 'open') returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not exists (select 1 from profiles where id = auth.uid() and is_admin) then raise exception 'admin only'; end if;
  return (select coalesce(jsonb_agg(jsonb_build_array(id, qid, reason, note, created_at) order by created_at desc), '[]')
    from (select * from q_reports where status = p_status order by created_at desc limit 500) r);
end $$;

-- Admin only: mark every open report on a question as fixed or dismissed.
create or replace function public.resolve_question_reports(p_qid text, p_status text) returns int
language plpgsql security definer set search_path = public as $$
declare k int;
begin
  if not exists (select 1 from profiles where id = auth.uid() and is_admin) then raise exception 'admin only'; end if;
  if p_status not in ('fixed', 'dismissed') then return 0; end if;
  update q_reports set status = p_status where qid = p_qid and status = 'open';
  get diagnostics k = row_count;
  return k;
end $$;

revoke execute on function public.report_question(text, text, text, text), public.question_reports_admin(text), public.resolve_question_reports(text, text) from public;
grant execute on function public.report_question(text, text, text, text) to anon, authenticated;
grant execute on function public.question_reports_admin(text), public.resolve_question_reports(text, text) to authenticated;
