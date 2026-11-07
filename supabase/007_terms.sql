-- 520 Quest Terms of Use acceptance: records on each account which Terms version the person accepted, and when.
-- Paste into Supabase > SQL Editor (dropdown next to Save = "Primary database") and click Run, after 001-006. Safe to run again.
--
-- Everyone accepts the Terms in the app before using it (free or paid). The app saves the acceptance on the device;
-- once the person signs in, it also calls accept_terms() so the account has a server-side record.

alter table public.profiles add column if not exists terms_version text;
alter table public.profiles add column if not exists terms_accepted_at timestamptz;

-- Users can't write these columns directly (only name, level, acc are granted); this function sets them for the caller only.
create or replace function public.accept_terms(p_version text, p_accepted_at timestamptz default null) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null or p_version is null or p_version !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' then return false; end if;
  update profiles
     set terms_version = p_version,
         -- trust the device's time only if it is recent and not in the future; otherwise use the server's time
         terms_accepted_at = case when p_accepted_at between now() - interval '400 days' and now() + interval '5 minutes' then p_accepted_at else now() end
   where id = auth.uid();
  return found;
end $$;
revoke all on function public.accept_terms(text, timestamptz) from public, anon;
grant execute on function public.accept_terms(text, timestamptz) to authenticated;
