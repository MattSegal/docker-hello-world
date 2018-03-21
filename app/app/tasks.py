from celery import shared_task

@shared_task
def echo():
    print("Celery works!")
