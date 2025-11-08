from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Promote user to superuser by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email address')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']

        try:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully promoted {email} to superuser')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} not found')
            )
