# Times Tables 50 — notes for future work (and future Claude chats)

Everything needed to keep working on the app is in this repository. Start a new chat by pointing Claude at this repo
and this file.

## The two versions

| Version | Where | Students' progress |
|---|---|---|
| **Claude version** (in use) | claude.ai artifact `https://claude.ai/artifact/BTCFrEjvzS8yHk9X8rxKND` (the old TEST artifact `XL5uS2rajkVUdnHqJW7Een` is retired, no longer updated) | Each student's browser only (save codes back it up) |
| **GitHub version** (testing, not for students until the school signs off) | `https://mrwiltshire-mb.github.io/Times-Tables-50/` + `teacher.html` | Supabase (Sydney), project `xovilczevfaqwhtuxsnw` |

## Files

- `claude-version/times-tables-live.html` — the source of truth: the app exactly as published. All changes are made here.
- `index.html`, `teacher.html` — the GitHub version, **built** by `build.py` from the live file + `src/`. Don't edit them by hand.
- `src/auth.js`, `src/app-cloud.js`, `src/teacher.html` — sign-in, online saving, teacher page.
- `setup.sql` — the whole database setup. `allow-*.sql`, `delete-students.sql` — changes already applied on top.
- `tests/checker/` — Playwright tests for the working-line checker and app features. They need a harness copy of the
  live file with `tests/checker/HARNESS-HOOK.js` inserted (never in a published file). The teacher code comes from the
  `TT_CODE` environment variable.
  Put `<meta charset="utf-8">` at the top of the harness copy: opened from disk, the browser can otherwise guess the
  wrong encoding (× shows as Ã—) and lines fail to read. Don't add it to the published file: claude.ai rejects a file
  that doesn't start with HTML it recognises, and serves it as UTF-8 anyway.
- `tests/github/` — tests for the GitHub version against a fake Supabase (`mock.py`).

## Workflow ("ptl": push to live, the default for every change)

Every change goes straight to live (there is no separate test artifact any more), so check it properly first:

1. Edit `times-tables-live.html`. Test it with the harness copy (tests in `tests/checker/`, screenshots of anything visual).
   For checker changes, run all the checker tests on the old and new file (same random seed) and compare the output.
2. Check: no `__tt`, no plain codes/PINs. Extract the `<script>` and run `node --check`.
3. Publish the live Claude artifact.
4. `python3 build.py <live file> out/` → copy `out/index.html`, `out/teacher.html` here, commit, push.

## Rules

- Only PBKDF2 hashes of codes/PINs go in any file. Never a plain code, in the app, this repo or replies.
- The Supabase publishable key in `src/auth.js` is meant to be public; the secret/service_role key must never be used.
- Pop-up boxes (`alert`/`confirm`/`prompt`) don't work inside the Claude artifact — use in-page confirms.

## Backups

- Code: this repository (GitHub keeps every version). Download a ZIP now and then (Code → Download ZIP).
- Claude version: the artifact keeps its version history in claude.ai.
- GitHub version student data: the free Supabase plan has **no automatic backups** — export regularly.
