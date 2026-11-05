-- 520 Quest owner admin: an account flag that unlocks everything, set only from the Supabase dashboard.
-- Paste into Supabase > SQL Editor and click Run (after 001_core.sql and 002_payments.sql). Safe to run again.
-- Nothing in the app can turn this on: signed-in users can update only name, level and acc (see 001_core.sql),
-- so the flag lives on the server, not in a code shipped to every browser.

alter table public.profiles add column if not exists is_admin boolean not null default false;

-- An admin counts as paid (3 devices) and gets every sheet and mnemonic, without needing a paid plan.
create or replace function public.is_paid(uid uuid default auth.uid()) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where id = uid and (plan <> 'free' or is_admin));
$$;
create or replace function public.has_full_access(uid uuid default auth.uid()) returns boolean
language sql stable security definer set search_path = public as $$
  -- Every paid plan (Monthly, 6 Months, Yearly) gets every sheet and mnemonic; so does an admin account.
  select exists (select 1 from public.profiles where id = uid and (plan in ('monthly', 'sixmonth', 'yearly') or is_admin));
$$;

-- To make an account admin, sign in to the app once with that email, then run (with your own email):
--   update public.profiles set is_admin = true where email = 'you@example.com';
-- To take it away:
--   update public.profiles set is_admin = false where email = 'you@example.com';
