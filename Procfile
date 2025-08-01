web: cd melkor_backend && gunicorn melkor_project.wsgi:application --bind 0.0.0.0:$PORT
release: cd melkor_backend && python manage.py migrate && python manage.py collectstatic --noinput
