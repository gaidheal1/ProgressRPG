# release: python manage.py test
web: gunicorn progress_rpg.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A progress_rpg worker --loglevel=info