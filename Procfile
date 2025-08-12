web: cd kermartin_backend && gunicorn kermartin_project.wsgi:application --bind 0.0.0.0:$PORT
release: cd kermartin_backend && python manage.py migrate && python manage.py collectstatic --noinput
