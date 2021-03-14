release: ./manage.py migrate --no-input
web: gunicorn flikcer.wsgi
worker: celery -A flikcer worker -l info --concurrency=1
