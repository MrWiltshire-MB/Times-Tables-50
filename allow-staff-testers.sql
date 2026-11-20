-- Let teachers make test accounts for staff (@education.vic.gov.au) as well as students.
-- Run once in Supabase: SQL Editor → New query → paste → Run.

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

