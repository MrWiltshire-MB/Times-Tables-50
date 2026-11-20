# Times Tables 50

Year 7 maths practice app (Maribyrnong College).

- `index.html`: the app. Students sign in with their school email; progress is saved in the browser and online (Supabase, Sydney).
- `teacher.html`: teacher page showing every student's progress (only for emails in the `teachers` table).
- `setup.sql`: database setup, run once in the Supabase SQL Editor.
- `src/` + `build.py`: sources. `build.py` makes `index.html` and `teacher.html` from the live app file.

Testing only: not for student use until the school has signed off.
