from celery import shared_task

from .models import Counter


@shared_task
def count():
	counter = Counter.objects.last()
	counter.count += 1
	counter.save()
