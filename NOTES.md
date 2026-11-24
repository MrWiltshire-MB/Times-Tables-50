# Times Tables 50 — notes for future work (and future Claude chats)

Everything needed to keep working on the app is in this repository. Start a new chat by pointing Claude at this repo
and this file.

## The two versions

| Version | Where | Students' progress |
|---|---|---|
| **Claude version** (in use) | claude.ai artifacts: LIVE `https://claude.ai/artifact/BTCFrEjvzS8yHk9X8rxKND`, TEST `https://claude.ai/artifact/XL5uS2rajkVUdnHqJW7Een` | Each student's browser only (save codes back it up) |
| **GitHub version** (testing, not for students until the school signs off) | `https://mrwiltshire-mb.github.io/Times-Tables-50/` + `teacher.html` | Supabase (Sydney), project `xovilczevfaqwhtuxsnw` |

## Files

- `claude-version/times-tables-test.html` — the source of truth. All changes are made here first.
- `claude-version/times-tables-live.html` — the same file with the test label removed (what's published live).
- `index.html`, `teacher.html` — the GitHub version, **built** by `build.py` from the live file + `src/`. Don't edit them by hand.
- `src/auth.js`, `src/app-cloud.js`, `src/teacher.html` — sign-in, online saving, teacher page.
- `setup.sql` — the whole database setup. `allow-*.sql`, `delete-students.sql` — changes already applied on top.
- `tests/checker/` — Playwright tests for the working-line checker and app features. They need a harness copy of the
  test file with `tests/checker/HARNESS-HOOK.js` inserted (never in a published file). The teacher code comes from the
  `TT_CODE` environment variable.
  Put `<meta charset="utf-8">` at the top of the harness copy: opened from disk, the browser can otherwise guess the
  wrong encoding (× shows as Ã—) and lines fail to read. Don't add it to the published file: claude.ai rejects a file
  that doesn't start with HTML it recognises, and serves it as UTF-8 anyway.
- `tests/github/` — tests for the GitHub version against a fake Supabase (`mock.py`).

## Workflow ("ptl": push to live, the default for every change)

1. Edit `times-tables-test.html`, test with the harness.
2. Live file = test file with `<title>Times Tables 50 Test</title>` → `<title>Times Tables 50</title>` and
   ` <small class="testtag">TEST</small>` removed. Check: no `testtag">TEST`, no `__tt`, no plain codes/PINs.
   Extract the `<script>` and run `node --check`.
3. Publish both Claude artifacts (live and test).
4. `python3 build.py <live file> out/` → copy `out/index.html`, `out/teacher.html` here, commit, push.

## Rules

- Only PBKDF2 hashes of codes/PINs go in any file. Never a plain code, in the app, this repo or replies.
- The Supabase publishable key in `src/auth.js` is meant to be public; the secret/service_role key must never be used.
- Pop-up boxes (`alert`/`confirm`/`prompt`) don't work inside the Claude artifact — use in-page confirms.

## Backups

- Code: this repository (GitHub keeps every version). Download a ZIP now and then (Code → Download ZIP).
- Claude version: the artifacts keep their version history in claude.ai.
- GitHub version student data: the free Supabase plan has **no automatic backups** — export regularly.
