import os
import time

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remind_me_django.settings')

app = Celery('remind_me_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks.py modules from all registered Django apps.
app.autodiscover_tasks()

# 'on_after_configure' is a signal to be sent after the celery app instance has *prepared* it's config settings.
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(5, test.s('hello'), name='add every 10')


@app.task
def test(arg):
    print(arg)


