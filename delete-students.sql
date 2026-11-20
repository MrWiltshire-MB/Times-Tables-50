-- Lets the teacher page delete student accounts.
-- Run once in Supabase: SQL Editor → New query → paste → Run.

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
