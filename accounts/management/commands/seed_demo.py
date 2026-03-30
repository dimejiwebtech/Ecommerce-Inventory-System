from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Seeds the database with test accounts'

    def handle(self, *args, **options):
        self.stdout.write('Seeding accounts...')
        
        # Admin Account (Superuser)
        admin_email = 'admin@aura.com'
        if not CustomUser.objects.filter(email=admin_email).exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email=admin_email,
                password='Testing123@',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Created Superuser: {admin_email} / Testing123@'))
        else:
            self.stdout.write(f'Admin {admin_email} already exists.')

        # Customer Account
        customer_email = 'customer@aura.com'
        if not CustomUser.objects.filter(email=customer_email).exists():
            CustomUser.objects.create_user(
                username='demo_customer',
                email=customer_email,
                password='Testing123@',
                first_name='Demo',
                last_name='Customer',
                role='customer',
                is_email_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created Customer: {customer_email} / Testing123@'))
        else:
            self.stdout.write(f'Customer {customer_email} already exists.')

        self.stdout.write(self.style.SUCCESS('Successfully seeded auth accounts!'))
