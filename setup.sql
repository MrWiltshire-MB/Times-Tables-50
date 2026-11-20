-- Times Tables 50: online accounts and progress.
-- Run once in Supabase: SQL Editor → New query → paste all of this → Run.
-- Before running, change the email on the last line to your own school email.

-- Teachers: anyone listed here can see every student's progress on the teacher page.
create table public.teachers (email text primary key);
alter table public.teachers enable row level security;
create policy "teachers see their own row" on public.teachers
  for select to authenticated using (lower(email) = lower(auth.jwt() ->> 'email'));
grant select on public.teachers to authenticated;

create or replace function public.is_teacher() returns boolean
  language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.teachers t where lower(t.email) = lower(auth.jwt() ->> 'email'));
$$;

-- Only school and Department emails (and anyone in the teachers list) can make an account.
create or replace function public.check_email_domain() returns trigger
  language plpgsql security definer set search_path = '' as $$
begin
  if lower(new.email) like '%@schools.vic.edu.au' or lower(new.email) like '%@education.vic.gov.au'
     or exists (select 1 from public.teachers t where lower(t.email) = lower(new.email)) then
    return new;
  end if;
  raise exception 'Only school email addresses can sign up';
end; $$;
create trigger check_email_domain before insert on auth.users
  for each row execute function public.check_email_domain();

-- Progress: one row per student. Students can only read and change their own row; teachers can read every row.
create table public.progress (
  user_id uuid primary key default auth.uid() references auth.users (id) on delete cascade,
  email text not null,
  name text,
  data jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.progress enable row level security;
create policy "read own progress, teachers read all" on public.progress
  for select to authenticated using (user_id = auth.uid() or public.is_teacher());
create policy "add own progress" on public.progress
  for insert to authenticated with check (user_id = auth.uid());
create policy "change own progress" on public.progress
  for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update on public.progress to authenticated;

-- The email and time on each row always come from the signed-in account, never from the app.
create or replace function public.progress_stamp() returns trigger
  language plpgsql security definer set search_path = '' as $$
begin
  new.email := lower(auth.jwt() ->> 'email');
  new.updated_at := now();
  return new;
end; $$;
create trigger progress_stamp before insert or update on public.progress
  for each row execute function public.progress_stamp();

revoke execute on function public.check_email_domain() from public, anon, authenticated;
revoke execute on function public.progress_stamp() from public, anon, authenticated;

-- You (change this to your email). Add other teachers the same way.
insert into public.teachers (email) values ('your.name@education.vic.gov.au');
