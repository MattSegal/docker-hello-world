#!/bin/bash
echo "Starting reddit app as `whoami`"

echo "Running migrations"
./manage.py migrate

# echo "Collecting static files."
# ./manage.py collectstatic --noinput

mkdir -p /var/log/gunicorn

echo "Starting gunicorn"
gunicorn reddit.wsgi:application \
  --name reddit \
  --workers 3 \
  --bind 0.0.0.0:8000 \
  --capture-output \
  --log-level info \
  --error-logfile /var/log/gunicorn/access.log \
  --access-logfile /var/log/gunicorn/error.log
