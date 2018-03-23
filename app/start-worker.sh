#!/bin/bash
BROKER="amqp://guest:guest@$CELERY_HOST:5672 "
celery worker --broker $BROKER --app reddit --loglevel info
