release: python manage.py migrate --noinput
web: python ./manage.py clear_cache && gunicorn pepysdiary.wsgi --preload
