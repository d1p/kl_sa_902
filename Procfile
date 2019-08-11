web: gunicorn config.wsgi --log-file -
worker: celery -A config.celery worker -B --loglevel=info
