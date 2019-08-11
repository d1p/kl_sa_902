web: gunicorn conf.wsgi --log-file -
worker: celery -A conf.celery worker -B --loglevel=info
