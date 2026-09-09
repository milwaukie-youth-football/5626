# 5626 (Quartz site) - project instructions

## Practice plans: always give the local URL

Whenever a practice plan file under `content/team/practice/` is created or
edited, end the response with its local preview URL. No exceptions, don't
wait to be asked.

- Dev server: Quartz's own (`npx quartz build --serve`), NOT a generic static
  file server.
- Check first whether it's already running: `ss -ltnp | grep -E ':(4173|8080)'`
  or `ps aux | grep quartz`. If one is up (with `--watch`), it picks up new/
  edited files automatically, no rebuild needed.
- If none is running, start one: `nohup npx quartz build --serve > /tmp/claude/quartz-serve.log 2>&1 & disown`
  (defaults to port 8080; an existing one from a prior session may be on a
  different port, e.g. 4173 - always check logs/`ss` for the real port
  instead of assuming 8080).
- URL pattern: `http://localhost:<port>/team/practice/<YYYY-MM-DD>/`
- Confirm it actually resolves (`curl -sI` → 200, following the 302 redirect
  from the no-trailing-slash form) before handing over the link - don't
  hand over an unverified guess.

## Known gotchas

- `npx quartz build --serve` fails with `EROFS ... /.npm/_npx/.../package-lock.json`
  under the default Bash sandbox (npx cache dir isn't in the write allowlist).
  Don't retry the same command - go straight to `dangerouslyDisableSandbox: true`
  for the `npx quartz` start command.
- `ss -ltnp` can show a stray `LISTEN 0.0.0.0:8080` with no matching PID from
  `ps`/`pgrep`/`fuser`/`lsof` (sandbox-namespace artifact, same family as the
  known phantom-file bug in `~/.claude/CLAUDE.md`). Don't burn time hunting
  for/killing it - it's not a real conflicting process. The port that matters
  is whatever an actual `ps aux | grep quartz` process is bound to.
