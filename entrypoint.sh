#!/usr/bin/env bash
set -e

# --- safely load .env (only KEY=VALUE lines, ignore comments) ---
if [ -f /code/.env ]; then
  while IFS='=' read -r key val; do
    # trim whitespace
    key="$(echo "$key" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    # only accept valid shell variable names and non-empty key
    if printf '%s' "$key" | grep -qE '^[A-Za-z_][A-Za-z0-9_]*$'; then
      # trim leading spaces from value + strip surrounding quotes
      val="$(echo "$val" | sed -e 's/^[[:space:]]*//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")"
      export "$key"="$val"
    fi
  done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' /code/.env || true)
fi

echo "Waiting for postgres (python socket check)..."
python - <<'PY'
import time, os, socket
host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", 5432))
s = socket.socket()
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except Exception:
        time.sleep(0.5)
PY

# Use the manage.py that lives under backend/
python backend/manage.py migrate --noinput

# collectstatic if needed (ignore failures)
python backend/manage.py collectstatic --noinput || true

# Optionally create superuser if env vars set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python backend/manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); \
username='$DJANGO_SUPERUSER_USERNAME'; \
email='$DJANGO_SUPERUSER_EMAIL'; \
password='$DJANGO_SUPERUSER_PASSWORD'; \
if not User.objects.filter(username=username).exists(): \
    User.objects.create_superuser(username=username,email=email,password=password)"
fi

# Start Gunicorn pointing to backend.wsgi, changing dir so imports resolve
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 3 --chdir backend
