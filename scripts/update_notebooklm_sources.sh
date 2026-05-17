#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
playbook="$repo_root/infra/notebooklm/update_notebooklm_sources.yml"

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "ansible-playbook is required to refresh NotebookLM sources." >&2
  exit 1
fi

exec ansible-playbook "$playbook" "$@"
