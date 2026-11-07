-- 520 Quest real MCAT results: students who took the real exam report their score, so the app's score range
-- can be checked and corrected against real outcomes.
-- Paste into Supabase > SQL Editor (dropdown next to Save = "Primary database") and click Run, after 001-005. Safe to run again.
--
-- Privacy: no user ids or emails are stored, only a random device id (made in the browser), the scores the student
-- typed, the month they tested, and what 520 Quest estimated for them at that moment. One result per device (a new
-- report replaces the old one).

create table if not exists public.mcat_results (
  dev text primary key,
  total int not null check (total between 472 and 528),
  cp int check (cp between 118 and 132),
  cars int check (cars between 118 and 132),
  bb int check (bb between 118 and 132),
  ps int check (ps between 118 and 132),
  test_month text,                               -- 'YYYY-MM'
  est jsonb not null default '{}',               -- {"CP":125,"CARS":126,...} app's mid estimate per section when reported
  answered int not null default 0,               -- questions answered in the app
  exams int not null default 0,                  -- full-length / mini exams finished in the app
  created_at timestamptz not null default now()
);
alter table public.mcat_results enable row level security;
revoke all on public.mcat_results from public, anon, authenticated; -- read and write only through the functions below

create or replace function public.report_mcat(p_dev text, p_total int, p_secs jsonb, p_month text, p_est jsonb, p_answered int, p_exams int) returns boolean
language plpgsql security definer set search_path = public as $$
declare v int; k text;
begin
  if p_dev is null or p_dev !~ '^[A-Za-z0-9-]{8,64}$' or p_total is null or p_total not between 472 and 528 then return false; end if;
  if p_month is not null and p_month !~ '^20[2-9][0-9]-(0[1-9]|1[0-2])$' then p_month := null; end if;
  if jsonb_typeof(p_secs) <> 'object' then p_secs := '{}'; end if;
  if jsonb_typeof(p_est) <> 'object' then p_est := '{}'; end if;
  foreach k in array array['CP', 'CARS', 'BB', 'PS'] loop
    if p_secs ? k then
      if jsonb_typeof(p_secs->k) <> 'number' then return false; end if;
      v := (p_secs->>k)::int;
      if v not between 118 and 132 then return false; end if;
    end if;
  end loop;
  insert into mcat_results as m (dev, total, cp, cars, bb, ps, test_month, est, answered, exams)
  values (p_dev, p_total, (p_secs->>'CP')::int, (p_secs->>'CARS')::int, (p_secs->>'BB')::int, (p_secs->>'PS')::int, p_month,
          p_est, greatest(coalesce(p_answered, 0), 0), greatest(coalesce(p_exams, 0), 0))
  on conflict (dev) do update set total = excluded.total, cp = excluded.cp, cars = excluded.cars, bb = excluded.bb, ps = excluded.ps,
    test_month = excluded.test_month, est = excluded.est, answered = excluded.answered, exams = excluded.exams, created_at = now();
  return true;
end $$;

-- Public: average (real - estimated) per section, from students who answered 300+ questions and had an estimate.
-- {"CP":[n, offset], ...}. The app only applies an offset once n >= 30.
create or replace function public.score_calibration() returns jsonb
language sql stable security definer set search_path = public as $$
  select coalesce(jsonb_object_agg(sec, jsonb_build_array(n, off)), '{}') from (
    select s.sec, count(*) as n, round(avg(s.real - s.est), 1) as off from (
      select 'CP' as sec, cp as real, (est->>'CP')::numeric as est from mcat_results where answered >= 300 and cp is not null and est ? 'CP'
      union all select 'CARS', cars, (est->>'CARS')::numeric from mcat_results where answered >= 300 and cars is not null and est ? 'CARS'
      union all select 'BB', bb, (est->>'BB')::numeric from mcat_results where answered >= 300 and bb is not null and est ? 'BB'
      union all select 'PS', ps, (est->>'PS')::numeric from mcat_results where answered >= 300 and ps is not null and est ? 'PS'
    ) s group by s.sec
  ) t;
$$;

-- Admin only: every result, newest first.
create or replace function public.mcat_results_admin() returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not exists (select 1 from profiles where id = auth.uid() and is_admin) then raise exception 'admin only'; end if;
  return (select coalesce(jsonb_agg(jsonb_build_array(total, cp, cars, bb, ps, test_month, est, answered, exams, created_at) order by created_at desc), '[]') from mcat_results);
end $$;

revoke execute on function public.report_mcat(text, int, jsonb, text, jsonb, int, int), public.score_calibration(), public.mcat_results_admin() from public;
grant execute on function public.report_mcat(text, int, jsonb, text, jsonb, int, int), public.score_calibration() to anon, authenticated;
grant execute on function public.mcat_results_admin() to authenticated;
