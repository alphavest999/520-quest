-- 520 Quest operations dashboard: one read-only function that hands the owner's dashboard its numbers.
-- Paste into Supabase > SQL Editor and click Run (after 001-007). Safe to run again.
--
-- Who can call it: only a signed-in account with profiles.is_admin = true (see 003_admin.sql).
-- Everyone else gets an error, so the dashboard HTML never needs a secret key: it signs in with the
-- same email code as the app and uses the public (publishable) key.
--
-- What it returns (the same shape as the DATA block at the top of 520-quest-dashboard.html):
--   users      from profiles + progress + devices (admin accounts are left out so they don't skew the numbers)
--   sessions   one row per user per day, from the app's daily log (progress.state.tlog: answered, correct, seconds)
--   examAttempts  from progress.state.examHist (finished full-lengths and minis, with dates)
--   payments   one row per new subscription from payment_events (live mode only). Renewals are not logged
--              there; import a Lemon Squeezy orders CSV in the dashboard for exact cash.
--   questions  percent correct per question from q_stats (no user ids, like the app's own stats)

create or replace function public.admin_dashboard() returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare
  v_ok boolean;
begin
  select is_admin into v_ok from public.profiles where id = auth.uid();
  if not coalesce(v_ok, false) then
    raise exception 'admins only' using errcode = '42501';
  end if;

  return jsonb_build_object(
    'asOf', to_char(now() at time zone 'America/New_York', 'YYYY-MM-DD'),

    'users', coalesce((
      select jsonb_agg(jsonb_build_object(
        'id', p.id,
        'name', coalesce(nullif(p.name, ''), split_part(coalesce(p.email, 'user'), '@', 1)),
        'email', p.email,
        'signup', to_char(p.created_at at time zone 'America/New_York', 'YYYY-MM-DD'),
        'plan', p.plan,
        'paidAt', case when p.plan <> 'free' then to_char(p.plan_since at time zone 'America/New_York', 'YYYY-MM-DD') end,
        'cancelledAt', case when p.plan = 'free' then (
            select to_char(max(e.event_time) at time zone 'America/New_York', 'YYYY-MM-DD')
            from public.payment_events e
            where e.user_id = p.id and e.plan = 'free' and not e.test_mode) end,
        'firstPaidAt', (
            select to_char(min(e.event_time) at time zone 'America/New_York', 'YYYY-MM-DD')
            from public.payment_events e
            where e.user_id = p.id and e.plan <> 'free' and not e.test_mode),
        'device', (select initcap(d.kind) from public.devices d where d.user_id = p.id order by d.last_seen desc limit 1),
        'xp', pr.state -> 'xp',
        'cat', pr.state -> 'cat',
        'badges', pr.state -> 'badges',
        'updated', to_char(pr.updated_at at time zone 'America/New_York', 'YYYY-MM-DD')
      ))
      from public.profiles p
      left join public.progress pr on pr.user_id = p.id
      where not p.is_admin
    ), '[]'::jsonb),

    'sessions', coalesce((
      select jsonb_agg(jsonb_build_object(
        'user', pr.user_id,
        'date', t.key,
        'questions', coalesce((t.value ->> 'n')::numeric, 0),
        'correct', coalesce((t.value ->> 'c')::numeric, 0),
        'minutes', round(coalesce((t.value ->> 's')::numeric, 0) / 60)
      ))
      from public.progress pr
      join public.profiles p on p.id = pr.user_id and not p.is_admin
      cross join lateral jsonb_each(case when jsonb_typeof(pr.state -> 'tlog') = 'object' then pr.state -> 'tlog' else '{}'::jsonb end) t
      where t.key ~ '^\d{4}-\d{2}-\d{2}$' and jsonb_typeof(t.value) = 'object'
    ), '[]'::jsonb),

    'examAttempts', coalesce((
      select jsonb_agg(jsonb_build_object(
        'user', pr.user_id,
        'exam', x.value ->> 'id',
        'date', case when jsonb_typeof(x.value -> 'date') = 'number'
                     then to_char(to_timestamp((x.value ->> 'date')::numeric / 1000) at time zone 'America/New_York', 'YYYY-MM-DD')
                     else to_char(pr.updated_at at time zone 'America/New_York', 'YYYY-MM-DD') end,
        'score', x.value -> 'total',
        'completed', true
      ))
      from public.progress pr
      join public.profiles p on p.id = pr.user_id and not p.is_admin
      cross join lateral jsonb_array_elements(case when jsonb_typeof(pr.state -> 'examHist') = 'array' then pr.state -> 'examHist' else '[]'::jsonb end) x
      where jsonb_typeof(x.value) = 'object'
    ), '[]'::jsonb),

    'payments', coalesce((
      select jsonb_agg(jsonb_build_object(
        'user', coalesce(e.user_id::text, (select p.id::text from public.profiles p where lower(p.email) = lower(e.email) limit 1)),
        'date', to_char(e.event_time at time zone 'America/New_York', 'YYYY-MM-DD'),
        'plan', e.plan
      ))
      from public.payment_events e
      where not e.test_mode and e.event_name = 'subscription_created' and e.plan <> 'free'
    ), '[]'::jsonb),

    'questions', coalesce((
      select jsonb_agg(jsonb_build_object(
        'id', q.qid,
        'attempts', q.n,
        'pctCorrect', round(100.0 * q.c / q.n, 1)
      ))
      from public.q_stats q
      where q.n > 0
    ), '[]'::jsonb)
  );
end;
$$;

revoke execute on function public.admin_dashboard() from public, anon;
grant execute on function public.admin_dashboard() to authenticated;
