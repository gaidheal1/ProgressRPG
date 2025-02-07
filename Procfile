web: gunicorn progress_rpg.wsgi:application --bind 0.0.0.0:8000
worker: celery -A progress_rpg worker --loglevel=info