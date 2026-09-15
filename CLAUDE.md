# 5626 (Quartz site) - project instructions

## ALWAYS give the local URL, every response, no exceptions

Every single response in this repo, whether or not a file changed this turn,
ends with the local preview URL for the relevant page (or the site root if
nothing specific applies). This is non-negotiable and has been missed before -
do not miss it again. No exceptions, don't wait to be asked, don't reason
your way out of it because "nothing changed" or "this file type isn't a
practice plan."

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

## After pushing to main: verify the live site, don't just assume

This repo auto-deploys to GitHub Pages via `.github/workflows/deploy.yml` on
every push to `main`. After any push:

- Check the run: `gh run list --repo milwaukie-youth-football/5626 --branch main --limit 1`
  - wait for `completed`/`success` before telling Scott it's live.
- Live URL: `https://milwaukie-youth-football.github.io/5626/<path>` -
  **no trailing slash** (GitHub Pages 404s with one; this is the opposite of
  the local dev server, which redirects the no-slash form TO the slash form).
- Confirm with `curl` that the live page actually contains the new content
  (grep for a distinctive string just added), not just a 200 - a stale cache
  can 200 on old content.
- Report both: the local preview URL (immediate) and the live GH Pages URL
  once the deploy run is green and content-checked.

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
- `git status`/`git add` under the default sandbox can surface bogus untracked
  files (`.bashrc`, `.bash_profile`, `.profile`, `.zprofile`, `.zshrc`,
  `.claude/`, `.mcp.json`, `.gitmodules`, `.idea`, `.vscode`, `.ripgreprc`) -
  same sandbox phantom-file bug as `~/.claude/CLAUDE.md` describes. Re-run
  `git status` with `dangerouslyDisableSandbox: true` to get the real list,
  and only ever `git add` specific files by name (never `-A`/`.`) in this
  repo.
- `git commit`/`add` can fail with `Unable to create .git/index.lock: File
  exists` from a stale lock (no live git process holding it). Check
  `ps aux | grep git` for an actual running git process first; if none, the
  lock is stale and clears itself (or is safe to remove) - don't treat it as
  uncommitted work to investigate.
