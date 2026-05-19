# swe-study-guide Deploy

Use this skill when the user wants the study site deployed, refreshed, restarted, or verified in production on the Hetzner VPS served over Tailscale.

Read first:
- `AGENTS.md`
- `README.md`
- `docs/INDEX.md`
- `serve.py`
- `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/swe_study_guide_setup.yml` on `automation/main` when the request includes the VPS
- `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/portal_setup.yml` on `automation/main` when Portal registration needs verification or repair
- `/Users/alex3m6/Dropbox/projects/automation/components/portal/config.yaml`
- `/Users/alex3m6/Dropbox/projects/automation/components/portal/catalog.yaml`

This repo and the VPS automation live in separate repositories:

- content and server code: `/Users/alex3m6/Dropbox/projects/swe-study-guide`
- VPS automation: `/Users/alex3m6/Dropbox/projects/automation`

Default behavior:

- treat "deploy" as a production service refresh via the automation repo, not as a GitHub release and not as a local preview refresh
- treat the Hetzner VPS as production and deploy `origin/main` only
- verify the service is still registered in the shared Portal on `:8087`, and update/redeploy the Portal if that registration is missing or stale
- after deploying, leave the primary local checkout on `main`
- if the current work is not merged to `main` yet, merge it first, push `main`, deploy from `main`, and then keep the primary local checkout on `main`

## When to use this skill

Use it for requests like:

- "deploy to the Hetzner VPS"
- "refresh the Tailscale site"
- "deploy this in production"
- "test the deploy in production"

Do not use this skill for skill deployment under `~/.codex/skills` or `~/.claude/skills`. That is handled by the repo playbook in `infra/ai-skills/deploy_ai_skills.yml` or `./scripts/deploy_ai_skills.sh`.

## Workflow

### 1. Treat deploy as production-only

Deploy requests for this repository should be handled as production deployments through the automation repo.

Rules:

- production must run `origin/main` only
- do not deploy `fix/*`, `feature/*`, detached commits, or unpushed local state to production
- do not satisfy a deploy request by refreshing `serve.py` locally
- if the needed fix is not on `main` yet, merge it to `main`, push `main`, deploy from `main`, and then leave the primary local checkout on `main`

### 2. Prepare `main` before deployment

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

Production deploys should happen only after these steps are complete. If the user wants a deploy but the work is still on a feature branch, finishing the deploy includes merging that work to `main`.

### 3. Hetzner VPS deployment

Use the automation repo playbook:

- playbook: `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/swe_study_guide_setup.yml`
- inventory: `/Users/alex3m6/Dropbox/projects/automation/infra/hetzner/inventory.local.ini`
- automation branch expectation: `main`

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

- The playbook itself should live on `automation/main`. If it is missing there, fix `automation/main` first instead of deploying from a side branch or temporary workaround.
- Do not override the branch for production deploys.
- If you changed only the `swe-study-guide` repo contents, push `main` before running the VPS deploy.
- If you changed the Hetzner playbook or service behavior in the `automation` repo, commit that repo too before considering the deployment workflow updated.
- Test production deploys using this Ansible workflow, not a local preview restart.

### 4. Verify the live VPS site

Verify:

- the Ansible run succeeds
- the play recap has no failures
- the reported Tailscale URL responds at `/health`
- the VPS checkout reports branch `main`
- if the user changed a topic, confirm `/api/content` or the relevant content endpoint reflects it

When checking the live VPS JSON, verify the exact technology or topic the user cares about instead of relying only on the HTML page.

### 5. Verify Portal registration

The SWE study guide should remain discoverable from the shared Portal on `http://100.84.173.75:8087/`.

Check both portal data sources in the automation repo:

- `/Users/alex3m6/Dropbox/projects/automation/components/portal/config.yaml`
- `/Users/alex3m6/Dropbox/projects/automation/components/portal/catalog.yaml`

If the service is missing or stale there, update the portal config/catalog and deploy the portal too:

- commit and push the relevant `automation` repo changes first, because the Portal reads its config and catalog from the deployed automation checkout on the VPS
- then run the portal playbook

```bash
cd /Users/alex3m6/Dropbox/projects/automation
git add components/portal/config.yaml components/portal/catalog.yaml infra/hetzner/templates/portal-config.local.yaml.j2
git commit -m "<message>"
git push origin main

cd /Users/alex3m6/Dropbox/projects/automation/infra/hetzner
ansible-playbook -i inventory.local.ini portal_setup.yml
```

Verify:

```bash
curl -sf http://100.84.173.75:8087/api/services
curl -sf http://100.84.173.75:8087/api/components
```

### 6. End state cleanup

After deployment:

- leave the primary local checkout on `main`
- make sure `main` is up to date with `origin/main`
- do not leave production pointing at a feature or fix branch
- do not leave the primary local checkout on the feature branch that was used during implementation

If a separate worktree or temporary branch was used, clean it up when the user is done with it.

## Common failure modes

- **VPS repo is current but the live site is stale** — the systemd service has not been restarted after content changes.
- **VPS deploy succeeds but the service cannot restart** — `serve.py` may have lost the `--host` flag or `/health` endpoint that the service and playbook expect.
- **The user is looking at a different port or older browser tab** — verify the exact URL and the JSON endpoint, not just the screenshot.
- **The study guide is live but missing from the Portal** — the Portal has separate service-card and component-catalog config. Update the portal config/catalog in the `automation` repo and redeploy `portal`.
- **The work is only on a feature branch** — merge to `main`, push `main`, and deploy from `main`; production deployment is not complete until that happens.

## Guardrails

- Do not claim the VPS is updated unless the relevant commit is pushed to `origin/main`.
- Do not deploy a non-`main` branch to production, even if the user is currently testing it locally.
- Do not leave the primary local checkout on a fix or feature branch after deployment unless the user explicitly asks for that.
- Do not rely on an `automation` feature branch or temp worktree for normal production deploys. Land the playbook on `automation/main` first.
- Do not use local preview as a substitute for production deployment testing.
- Do not edit installed skill copies under `~/.codex/skills` or `~/.claude/skills` by hand.
- Treat the `automation` repo as a separate codebase with its own git state. Do not sweep unrelated untracked files into a deploy-fix commit.

## Output expectations

Report:

- that production was deployed through the automation Ansible playbook
- the Tailscale URL
- the branch and commit verified on the VPS
- the verification you performed
- whether Portal registration was verified or updated
- whether the primary local checkout was returned to `main`
