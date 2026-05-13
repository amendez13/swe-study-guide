# CI Runner Operations

This guide documents how the template chooses between GitHub-hosted and self-hosted runners, how CI provisions its Python toolchain, and what you need to provision if you want to run CI on your own hardware.

## When To Use Which Runner

### GitHub-hosted

Use `github_hosted` when:

- you want the lowest-setup path
- your project does not need persistent self-hosted infrastructure
- you want GitHub to manage runner lifecycle and OS patching

### Self-hosted

Use `self_hosted_linux` or `self_hosted_linux_arm64` when:

- you need a fixed machine, architecture, or private network access
- you need parity with deployment hardware or ARM-specific behavior
- you want to keep optional Docker-based troubleshooting or local parity tooling nearby

## Runner-As-Execution Guidance

The main CI workflow installs its Python toolchain inside each job. The runner should be treated as a thin host that only needs to:

- run GitHub Actions jobs
- provide the requested runner labels
- allow outbound network access for dependency installation

That means:

- GitHub-hosted CI and self-hosted CI execute the same workflow steps
- "works on my machine" should map to "works in CI" when you validate with the same Python commands from `docs/CI.md`
- host-specific setup belongs in runner bootstrap playbooks, not in individual CI jobs

The optional Docker CI image is still useful for local troubleshooting, but GitHub Actions no longer requires that image to exist in GHCR.

## Workflow Surface

`ci.yml` resolves runner selection centrally:

- default target: `github_hosted`
- manual override via `workflow_dispatch` input `runner_target`
- supported values:
  - `github_hosted`
  - `self_hosted_linux`
  - `self_hosted_linux_arm64`

Downstream jobs consume:

- `runs-on: ${{ fromJSON(needs.resolve-runner.outputs.runner) }}`

## Register A Self-Hosted Runner

1. Create a Linux host that can run the GitHub Actions runner.
2. Create a GitHub runner registration token for the repository.
3. Copy and adapt `infra/home-worker/ci_runner_setup.yml` for your environment.
4. Keep the runner labels aligned with `.github/workflows/ci.yml`.
5. Optionally install Docker if you want local container-based parity checks.

Suggested baseline labels:

- `self-hosted`
- `linux`

Add `arm64` if the host should satisfy the ARM-specific target.

## Use The Optional Docker CI Image Locally

```bash
docker build -t swe-study-guide-ci:test -f infra/ci/Dockerfile .
docker compose -f infra/ci/docker-compose.ci.yml run --rm ci bash
```

Inside the container, run the same commands CI uses:

```bash
python3.12 -m pytest tests/ -v --cov=src
bandit -r src/ -ll
pip-audit --requirement requirements.txt
```

## Bootstrap Checklist For Self-Hosted Linux

- install the GitHub Actions runner binary for the host architecture
- register the runner for `https://github.com/alex3m6/swe-study-guide`
- configure the runner as a persistent service
- verify the runner can complete outbound package installs during a CI run
- run a manual `workflow_dispatch` CI job against the self-hosted target

## Operational Notes

- If you rename CI jobs, update the required status contexts in `scripts/github/branch-protection-config.json`.
- If you change runner labels, keep `docs/CI_RUNNER.md`, `infra/home-worker/ci_runner_setup.yml`, and `.github/workflows/ci.yml` aligned.
- If you change the optional containerized toolchain, rebuild the CI image before expecting local Docker parity checks to pick it up.
