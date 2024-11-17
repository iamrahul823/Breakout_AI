# celery.py

from celery import Celery

# Create a Celery instance with Redis as the message broker
app = Celery('email_scheduler', broker='redis://localhost:6379/0')

# Celery configuration
app.conf.result_backend = 'redis://localhost:6379/0'


# tasks.py

from celery import shared_task
from .email_utils import send_email  # Assuming you have email sending logic in this file

@shared_task
def send_email_task(sender, to, subject, body):
    # Send email using Gmail API or any other service
    send_email(sender, to, subject, body)
