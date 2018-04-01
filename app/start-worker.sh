#!/bin/bash
BROKER="amqp://guest:guest@$CELERY_HOST:5672 "
celery worker \
	--broker $BROKER \
	--app reddit \
	--logfile /var/log/celery.log
	--loglevel info
