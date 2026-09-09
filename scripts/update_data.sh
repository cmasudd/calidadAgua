#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ -n "$(git status --porcelain --untracked-files=normal -- . ':!data' ':!data-update.log')" ]]; then
  echo "Hay cambios manuales sin commit" >&2
  exit 1
fi
git pull --ff-only
/var/www/api_sensores/venv/bin/python scripts/export_monthly_csv.py
git add data
if ! git diff --cached --quiet; then
  git -c user.name='CMAS Data Publisher' -c user.email='cmas-data@users.noreply.github.com' commit -m "data: actualización horaria"
fi
git push origin main
