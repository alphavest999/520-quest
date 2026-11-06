-- 520 Quest question stats: the real percent of students who get each question right.
-- Paste into Supabase > SQL Editor (dropdown next to Save = "Primary database") and click Run, after 001-003. Safe to run again.
--
-- Privacy: no user ids or emails are stored. Each answer carries only a random device id (made in the browser),
-- the question id, the option picked, and right/wrong. Only a device's FIRST answer to a question counts,
-- so retakes and spam from one device can't skew a question.
-- Anyone can send answers and read the percent for questions with 30+ answers; only an admin account sees the full table.

create table if not exists public.q_stats (
  qid text primary key,
  n int not null default 0,                     -- first-time answers
  c int not null default 0,                     -- of those, correct
  picks int[] not null default '{0,0,0,0}',     -- how often each option was picked (A-D, original order, before shuffling)
  updated_at timestamptz not null default now()
);
create table if not exists public.q_seen (
  dev text not null,
  qid text not null,
  primary key (dev, qid)
);
alter table public.q_stats enable row level security;
alter table public.q_seen enable row level security;
revoke all on public.q_stats, public.q_seen from public, anon, authenticated; -- read and write only through the functions below

-- The app sends a small batch: [{"q":"BB_123","k":1,"ok":false}, ...]. k is the option index 0-3 (null if time ran out).
create or replace function public.record_answers(p_dev text, p_items jsonb) returns int
language plpgsql security definer set search_path = public as $$
declare it jsonb; v_q text; v_k int; v_ok boolean; added int := 0;
begin
  if p_dev is null or p_dev !~ '^[A-Za-z0-9-]{8,64}$' or jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) > 50 then return 0; end if;
  for it in select * from jsonb_array_elements(p_items) loop
    v_q := it->>'q';
    continue when v_q is null or v_q !~ '^[A-Za-z0-9_.-]{1,64}$' or jsonb_typeof(it->'ok') <> 'boolean';
    v_ok := (it->>'ok')::boolean;
    v_k := case when jsonb_typeof(it->'k') = 'number' and (it->>'k') in ('0', '1', '2', '3') then (it->>'k')::int else null end;
    insert into q_seen (dev, qid) values (p_dev, v_q) on conflict do nothing;
    continue when not found;
    insert into q_stats as s (qid, n, c, picks) values (v_q, 1, v_ok::int,
        array[coalesce((v_k = 0)::int, 0), coalesce((v_k = 1)::int, 0), coalesce((v_k = 2)::int, 0), coalesce((v_k = 3)::int, 0)])
      on conflict (qid) do update set n = s.n + 1, c = s.c + v_ok::int,
        picks = case when v_k is null then s.picks else
          array[s.picks[1] + (v_k = 0)::int, s.picks[2] + (v_k = 1)::int, s.picks[3] + (v_k = 2)::int, s.picks[4] + (v_k = 3)::int] end,
        updated_at = now();
    added := added + 1;
  end loop;
  return added;
end $$;

-- What students see after answering: percent correct, only once a question has at least 30 answers.
-- One JSON object {"BB_123": [answers, percent], ...} so the app gets everything in one small request.
create or replace function public.question_rates() returns jsonb
language sql stable security definer set search_path = public as $$
  select coalesce(jsonb_object_agg(qid, jsonb_build_array(n, round(100.0 * c / n)::int)), '{}') from q_stats where n >= 30;
$$;

-- Admin only: every question with at least p_min answers, hardest first, as [[qid, answers, correct, picks], ...].
create or replace function public.question_stats_admin(p_min int default 20) returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not exists (select 1 from profiles where id = auth.uid() and is_admin) then raise exception 'admin only'; end if;
  return (select coalesce(jsonb_agg(jsonb_build_array(qid, n, c, picks) order by c::numeric / n, n desc), '[]')
    from q_stats where n >= greatest(p_min, 1));
end $$;

revoke execute on function public.record_answers(text, jsonb), public.question_rates(), public.question_stats_admin(int) from public;
grant execute on function public.record_answers(text, jsonb), public.question_rates() to anon, authenticated;
grant execute on function public.question_stats_admin(int) to authenticated;
