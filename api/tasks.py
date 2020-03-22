import os
import csv

from celery import task
from django.conf import settings
from django.utils import timezone

from users.models import CustomUser


EXPORT_FILE = 'data.csv'
EXPORT_PATH = os.path.join(settings.STATIC_ROOT, EXPORT_FILE)


FIELDNAMES = ['timestamp', 'user_id', 'lon', 'lat', 'category', 'contacts']


@task(name='export')
def export():
    timestamp = timezone.now()

    if not os.path.isfile(EXPORT_PATH):
        with open(EXPORT_PATH, 'w+') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

    with open(EXPORT_PATH, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        for user in CustomUser.objects.all():
            contacts = [contact.randomized_id for contact in user._contacts.all()]
            category = user.category
            severity = category.severity if category is not None else None
            data = {
                'user_id': user.randomized_id,
                'lon': user.lon,
                'lat': user.lat,
                'category': severity,
                'contacts': contacts,
                'timestamp': timestamp,
            }
            writer.writerow(data)
