# swe-study-guide Deploy

Use this skill when the user wants the study site deployed, refreshed, restarted, or verified either:

- locally from the current checkout
- on the Hetzner VPS served over Tailscale

Read first:
- `AGENTS.md`
- `README.md`
- `docs/INDEX.md`
- `serve.py`
- `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/swe_study_guide_setup.yml` when the request includes the VPS

This repo and the VPS automation live in separate repositories:

- content and server code: `/Users/alex3m6/Dropbox/projects/swe-study-guide`
- VPS automation: `/Users/alex3m6/Dropbox/projects/automation`

Default behavior:

- treat "deploy" as a preview refresh or VPS service refresh, not as a GitHub release
- prefer reusing `127.0.0.1:8766` for local preview when the user is already using that URL
- verify both the JSON API and the browser-facing site after restarting
- treat the Hetzner VPS as production and deploy `origin/main` only
- after completing a fix delivery, return the primary local checkout to `main`

## When to use this skill

Use it for requests like:

- "deploy the site locally"
- "restart the preview server"
- "make localhost show the latest changes"
- "deploy to the Hetzner VPS"
- "refresh the Tailscale site"
- "the topic exists on disk but the technology page doesn't show it"

Do not use this skill for skill deployment under `~/.codex/skills` or `~/.claude/skills`. That is handled by the repo playbook in `infra/ai-skills/deploy_ai_skills.yml` or `./scripts/deploy_ai_skills.sh`.

## Workflow

### 1. Decide the deployment target

Identify which target the user wants:

- local preview only
- Hetzner VPS only
- both local preview and Hetzner VPS

If the user asks for the Hetzner VPS, remember:

- production must run `origin/main` only
- do not deploy `fix/*`, `feature/*`, detached commits, or unpushed local state to production
- if the needed fix is not on `main` yet, merge it to `main`, push `main`, then deploy

### 2. Check whether a local server is already listening

Run:

```bash
lsof -nP -iTCP:8766 -sTCP:LISTEN || true
```

If another `serve.py` process is already listening on the target port, assume it may have a stale in-memory index. `serve.py` builds the content index only at startup.

### 3. Verify whether the running local server is stale

Check the local JSON API first:

```bash
python3 - <<'PY'
import json, urllib.request
payload = json.load(urllib.request.urlopen('http://127.0.0.1:8766/api/content'))
print([tech["dir"] for tech in payload["technologies"]])
PY
```

If the expected technology or topic is missing from `/api/content` but the raw file is reachable under `/content/...`, the server is stale and needs a restart.

### 4. Restart `serve.py` for local preview

Use the repo-local `serve.py` server.

If an old process is listening, stop it first. Then start the server from the repository root.

Typical command pattern:

```bash
python3 -u serve.py --host 127.0.0.1 --port 8766
```

Use a foreground session when you need reliable verification right away. Detached starts can hide startup failures.

If you must run it in the background, capture logs somewhere explicit and confirm the process is still listening before telling the user it worked.

Notes:

- `serve.py` must keep supporting `--host` and `/health`; the VPS deployment depends on that contract.
- Prefer verifying the specific changed technology or topic rather than only checking the homepage.

### 5. Verify the refreshed local site

Check:

- `http://127.0.0.1:8766/health`
- `http://127.0.0.1:8766/api/content`
- the relevant `/content/<technology>/<topic>/...` endpoint for the user's change

If browser automation is available, verify the browser-facing page too. A missing `favicon.ico` 404 is harmless and should not be treated as a deployment failure.

### 6. Prepare for Hetzner VPS deployment

Before deploying production:

1. make sure the desired fix is committed
2. merge the fix onto local `main`
3. push `main` to `origin/main`
4. confirm the primary checkout is on `main`

If the current local checkout is still on a fix branch after the work is done, switch it back:

```bash
git checkout main
git pull --ff-only origin main
```

Production deploys should happen only after these steps are complete.

### 7. Hetzner VPS deployment

Use the automation repo playbook:

- playbook: `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/swe_study_guide_setup.yml`
- inventory: `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/inventory.local.ini`

Run from:

```bash
cd /Users/alex3m6/Dropbox/projects/automation/infra/hetzner
ansible-playbook -i inventory.local.ini swe_study_guide_setup.yml
```

What this playbook does:

- updates `/home/admin/projects/swe-study-guide` on the VPS from `origin/main`
- ensures the virtualenv dependencies are installed
- installs the `swe-study-guide.service` systemd unit
- restarts the service when repo content, dependency state, or unit contents change
- verifies the service is active
- verifies the Tailscale health endpoint

Important:

- Do not override the branch for production deploys.
- If you changed only the `swe-study-guide` repo contents, push `main` before running the VPS deploy.
- If you changed the Hetzner playbook or service behavior in the `automation` repo, commit that repo too before considering the deployment workflow updated.

### 8. Verify the live VPS site

Verify:

- the Ansible run succeeds
- the play recap has no failures
- the reported Tailscale URL responds at `/health`
- the VPS checkout reports branch `main`
- if the user changed a topic, confirm `/api/content` or the relevant content endpoint reflects it

When checking the live VPS JSON, verify the exact technology or topic the user cares about instead of relying only on the HTML page.

### 9. End state cleanup

After the fix is delivered:

- leave the primary local checkout on `main`
- make sure `main` is up to date with `origin/main`
- do not leave production pointing at a feature or fix branch

If a separate worktree or temporary branch was used, clean it up when the user is done with it.

## Common failure modes

- **Port already in use** — another local preview is still running.
- **Local content file loads but sidebar JSON is stale** — the old `serve.py` process was not restarted after content changes.
- **Detached local restart silently dies** — rerun `python3 -u serve.py --host 127.0.0.1 --port <port>` in the foreground to see the real startup error.
- **VPS repo is current but the live site is stale** — the systemd service has not been restarted after content changes.
- **VPS deploy succeeds but the service cannot restart** — `serve.py` may have lost the `--host` flag or `/health` endpoint that the service and playbook expect.
- **The user is looking at a different port or older browser tab** — verify the exact URL and the JSON endpoint, not just the screenshot.

## Guardrails

- Do not claim the VPS is updated unless the relevant commit is pushed to `origin/main`.
- Do not deploy a non-`main` branch to production, even if the user is currently testing it locally.
- Do not leave the primary local checkout on a fix branch after the fix is finished unless the user explicitly asks for that.
- Do not edit installed skill copies under `~/.codex/skills` or `~/.claude/skills` by hand.
- Do not assume a running local server is current; verify `/api/content` or the changed content endpoint.
- Treat the `automation` repo as a separate codebase with its own git state. Do not sweep unrelated untracked files into a deploy-fix commit.

## Output expectations

Report:

- which target(s) were deployed
- the local URL and/or Tailscale URL
- the branch and commit verified on the VPS
- the verification you performed
- whether the primary local checkout was returned to `main`
