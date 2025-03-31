release: python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT progress_rpg.asgi:application 
worker: python manage.py runworker default
# celery: celery -A progress_rpg worker --loglevel=info