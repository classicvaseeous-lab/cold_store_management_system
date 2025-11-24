from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    help = "Create a default superuser if none exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = "Frank"
        password = "Frank@0707@"
        email = "frankadiamah07@gmail.com"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS("Superuser created"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
