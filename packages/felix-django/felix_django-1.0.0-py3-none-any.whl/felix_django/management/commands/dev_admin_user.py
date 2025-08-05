import logging
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        password = os.environ['APP_ADMIN_PASSWORD']
        user_model = get_user_model()
        admin, _ = user_model.objects.update_or_create(
            username='admin',
            email='admin@example.org',
        )
        admin.is_superuser = True
        admin.is_staff = True
        admin.set_password(password)
        admin.save()
