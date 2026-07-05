#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# Deploy script for curasuite.app
# Usage: ./deploy.sh
# ─────────────────────────────────────────────────────────────────
set -e  # stop immediately on any error

APP_DIR="/home/deploy/apps/curasuite"
ENV_FILE="/etc/curasuite/env/curasuite.env"
SERVICE_NAME="curasuite"
SETTINGS_MODULE="config.settings.production"

cd "$APP_DIR"

echo "── Checking for uncommitted local changes ──"
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Local changes detected on the server:"
    git status --short
    echo ""
    echo "Refusing to pull automatically — resolve or commit these first."
    echo "Run 'git diff' to review, then either commit+push or discard before re-running this script."
    exit 1
fi

echo "── Fetching latest changes ──"
git fetch origin

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Already up to date. Nothing to deploy."
    exit 0
fi

echo "── Changes incoming ──"
git log HEAD..origin/main --oneline
echo ""
echo "── Files changed ──"
git diff HEAD origin/main --stat
echo ""

CHANGED_FILES=$(git diff HEAD origin/main --name-only)
if echo "$CHANGED_FILES" | grep -qE "config/settings/|config/__init__.py|requirements"; then
    echo "⚠️  WARNING: incoming changes touch settings or requirements files."
    echo "   Review these carefully after pulling — past incidents on this project"
    echo "   involved Celery/Redis settings being silently reintroduced."
    echo ""
    read -p "Continue with pull? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted by user."
        exit 1
    fi
fi

echo "── Pulling ──"
git pull origin main

echo "── Activating venv ──"
source venv/bin/activate

if echo "$CHANGED_FILES" | grep -q "requirements.txt"; then
    echo "── requirements.txt changed — reinstalling dependencies ──"
    pip install -r requirements.txt
else
    echo "── requirements.txt unchanged — skipping pip install ──"
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"

echo "── Checking Django configuration before touching the database ──"
python manage.py check --deploy

echo "── Running migrations ──"
python manage.py migrate

echo "── Collecting static files ──"
python manage.py collectstatic --noinput

echo "── Restarting service ──"
sudo systemctl restart "$SERVICE_NAME"
sleep 2
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "── Smoke test ──"
sleep 1
curl -sI https://curasuite.app | head -1

echo ""
echo "✅ Deploy complete."
