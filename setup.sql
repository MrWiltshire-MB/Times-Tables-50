-- Times Tables 50: accounts and online progress.
-- Run once in Supabase: SQL Editor → New query → paste all of this → Run.
-- Before running, change the email on the last line to your own email.
--
-- How accounts work: teachers make student accounts on the teacher page (no emails are sent).
-- Students can't sign themselves up. Teachers' own accounts are made in the Supabase dashboard
-- (Authentication → Users → Add user → Create new user, with "Auto Confirm User" ticked).

create extension if not exists pgcrypto with schema extensions;

-- Teachers: anyone listed here can see every student's progress and make student accounts.
create table public.teachers (email text primary key);
alter table public.teachers enable row level security;
create policy "teachers see their own row" on public.teachers
  for select to authenticated using (lower(email) = lower(auth.jwt() ->> 'email'));
grant select on public.teachers to authenticated;

create or replace function public.is_teacher() returns boolean
  language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.teachers t where lower(t.email) = lower(auth.jwt() ->> 'email'));
$$;

-- Only school and Department emails (and anyone in the teachers list) can have an account.
create or replace function public.check_email_domain() returns trigger
  language plpgsql security definer set search_path = '' as $$
begin
  if lower(new.email) like '%@schools.vic.edu.au' or lower(new.email) like '%@education.vic.gov.au'
     or exists (select 1 from public.teachers t where lower(t.email) = lower(new.email)) then
    return new;
  end if;
  raise exception 'Only school email addresses can have an account';
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

-- Teacher page: make a student account with a password (no email is sent).
-- Staff (@education.vic.gov.au) can be given test accounts the same way.
create or replace function public.teacher_add_student(student_email text, student_password text) returns text
  language plpgsql security definer set search_path = '' as $$
declare
  e text := lower(trim(student_email));
  uid uuid := gen_random_uuid();
begin
  if not public.is_teacher() then raise exception 'Teachers only'; end if;
  if e !~ '^[^@[:space:]]+@(schools\.vic\.edu\.au|education\.vic\.gov\.au)$' then return 'not a school email'; end if;
  if length(student_password) < 8 then return 'password too short'; end if;
  if exists (select 1 from auth.users u where lower(u.email) = e) then return 'exists'; end if;
  insert into auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at,
      raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
      confirmation_token, recovery_token, email_change_token_new, email_change)
    values ('00000000-0000-0000-0000-000000000000', uid, 'authenticated', 'authenticated', e,
      extensions.crypt(student_password, extensions.gen_salt('bf')), now(),
      '{"provider":"email","providers":["email"]}', '{}', now(), now(), '', '', '', '');
  insert into auth.identities (id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
    values (gen_random_uuid(), uid, uid::text,
      jsonb_build_object('sub', uid::text, 'email', e, 'email_verified', true), 'email', now(), now(), now());
  return 'created';
end; $$;

-- Teacher page: give a student a new password (for a forgotten one)
create or replace function public.teacher_set_password(student_email text, student_password text) returns text
  language plpgsql security definer set search_path = '' as $$
declare e text := lower(trim(student_email));
begin
  if not public.is_teacher() then raise exception 'Teachers only'; end if;
  if e !~ '^[^@[:space:]]+@(schools\.vic\.edu\.au|education\.vic\.gov\.au)$' then return 'not a school email'; end if;
  if length(student_password) < 8 then return 'password too short'; end if;
  update auth.users set encrypted_password = extensions.crypt(student_password, extensions.gen_salt('bf')), updated_at = now()
    where lower(email) = e;
  if not found then return 'no account'; end if;
  return 'done';
end; $$;

-- Teacher page: every student account, including ones that haven't signed in yet
create or replace function public.teacher_list_students()
  returns table (email text, created_at timestamptz, last_sign_in_at timestamptz)
  language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_teacher() then raise exception 'Teachers only'; end if;
  return query select lower(u.email)::text, u.created_at, u.last_sign_in_at from auth.users u
    where (lower(u.email) like '%@schools.vic.edu.au' or lower(u.email) like '%@education.vic.gov.au')
      and not exists (select 1 from public.teachers t where lower(t.email) = lower(u.email))
    order by 1;
end; $$;

-- Teacher page: delete a student's account and all their progress (can't be undone)
create or replace function public.teacher_delete_student(student_email text) returns text
  language plpgsql security definer set search_path = '' as $$
declare e text := lower(trim(student_email));
begin
  if not public.is_teacher() then raise exception 'Teachers only'; end if;
  if e !~ '^[^@[:space:]]+@(schools\.vic\.edu\.au|education\.vic\.gov\.au)$' then return 'not a school email'; end if;
  if exists (select 1 from public.teachers t where lower(t.email) = e) then return 'teacher accounts can only be deleted in Supabase'; end if;
  delete from public.progress where lower(email) = e;
  delete from auth.users where lower(email) = e;
  if not found then return 'no account'; end if;
  return 'deleted';
end; $$;
revoke execute on function public.teacher_delete_student(text) from public, anon;
grant execute on function public.teacher_delete_student(text) to authenticated;

revoke execute on function public.check_email_domain() from public, anon, authenticated;
revoke execute on function public.progress_stamp() from public, anon, authenticated;
revoke execute on function public.teacher_add_student(text, text) from public, anon;
revoke execute on function public.teacher_set_password(text, text) from public, anon;
revoke execute on function public.teacher_list_students() from public, anon;
grant execute on function public.teacher_add_student(text, text) to authenticated;
grant execute on function public.teacher_set_password(text, text) to authenticated;
grant execute on function public.teacher_list_students() to authenticated;

-- You (change this to your email). Add other teachers the same way.
insert into public.teachers (email) values ('your.name@education.vic.gov.au');
