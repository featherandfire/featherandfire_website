import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or update a superuser from ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD env vars.'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME')
        email = os.getenv('ADMIN_EMAIL')
        password = os.getenv('ADMIN_PASSWORD')

        if not (username and password):
            self.stdout.write('bootstrap_admin: ADMIN_USERNAME and/or ADMIN_PASSWORD not set; skipping.')
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={'email': email or ''})
        if email:
            user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        verb = 'created' if created else 'updated'
        self.stdout.write(f'bootstrap_admin: superuser {username!r} {verb}.')
