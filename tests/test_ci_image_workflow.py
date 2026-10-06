"""Regression coverage for the repository-owned CI image publisher."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_ci_image_publishes_under_current_repository_and_rebuilds_on_workflow_change() -> None:
    """A repository transfer must not retain the previous owner's GHCR tags."""
    workflow = yaml.load((ROOT / ".github/workflows/ci-image.yml").read_text(), Loader=yaml.BaseLoader)
    assert ".github/workflows/ci-image.yml" in workflow["on"]["push"]["paths"]
    steps = workflow["jobs"]["build-and-push"]["steps"]
    build = next(step for step in steps if step["name"] == "Build and push image")
    assert build["with"]["tags"].splitlines() == [
        "ghcr.io/${{ github.repository }}-ci:latest",
        "ghcr.io/${{ github.repository }}-ci:${{ github.sha }}",
    ]
    assert set(build["with"]["platforms"].split(",")) == {"linux/amd64", "linux/arm64"}
    assert build["with"]["push"] == "true"


def test_local_ci_image_defaults_match_current_repository() -> None:
    """Local publishing and runner provisioning use the same image namespace."""
    image = "ghcr.io/amendez13/swe-study-guide-ci"
    script = (ROOT / "infra/ci/build-and-push.sh").read_text()
    assert f'REPO="${{REPO:-{image}}}"' in script
    runner = yaml.safe_load((ROOT / "infra/home-worker/ci_runner_setup.yml").read_text())
    assert runner[0]["vars"]["ci_runner_image"] == f"{image}:latest"
