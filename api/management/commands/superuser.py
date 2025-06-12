from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a superuser for the custom user model.'

    def handle(self, *args, **options):
        User = get_user_model()
        # Hardcoded credentials
        email = 'inquiry@pragathifs.com'
        password = 'Pragathi@2020'
        name = 'Admin User'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(
                f"Superuser with email {email} already exists."))
            return

        user = User.objects.create_superuser(
            email=email, password=password, name=name)
        user.is_active = True
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Superuser created with email: {email}"))
