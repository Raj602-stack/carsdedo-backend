web: gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --chdir backend --workers 3 --timeout 120
release: python backend/manage.py migrate --noinput && python backend/manage.py collectstatic --noinput
