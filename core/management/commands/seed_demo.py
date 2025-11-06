from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random
from decimal import Decimal

from core.models import User
from services.models import Service, ServiceItem
from inventory.models import Item
from appointments.models import Appointment, AppointmentSettings, BlockedRange
from payments.models import Payment
from chatbot.models import Rule


class Command(BaseCommand):
    help = 'Seed database with demo data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        with transaction.atomic():
            # Create users
            self.stdout.write('Creating users...')
            users = self.create_users()

            # Create inventory items
            self.stdout.write('Creating inventory items...')
            items = self.create_inventory()

            # Create services
            self.stdout.write('Creating services...')
            services = self.create_services(items)

            # Create appointment settings
            self.stdout.write('Creating appointment settings...')
            self.create_appointment_settings()

            # Create blocked ranges
            self.stdout.write('Creating blocked ranges...')
            self.create_blocked_ranges()

            # Create appointments
            self.stdout.write('Creating appointments...')
            appointments = self.create_appointments(users['customers'], services)

            # Create payments
            self.stdout.write('Creating payments...')
            self.create_payments(appointments)

            # Create chatbot rules
            self.stdout.write('Creating chatbot rules...')
            self.create_chatbot_rules()

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def clear_data(self):
        """Clear existing demo data."""
        Payment.objects.all().delete()
        Appointment.objects.all().delete()
        BlockedRange.objects.all().delete()
        ServiceItem.objects.all().delete()
        Service.objects.all().delete()
        Item.objects.all().delete()
        Rule.objects.all().delete()
        User.objects.filter(email__in=[
            'admin@dreambook.com',
            'staff@dreambook.com',
            'customer1@example.com',
            'customer2@example.com',
            'customer3@example.com',
        ]).delete()

    def create_users(self):
        """Create demo users."""
        admin = User.objects.create_user(
            email='admin@dreambook.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )

        staff = User.objects.create_user(
            email='staff@dreambook.com',
            password='staff123',
            first_name='Staff',
            last_name='Member',
            role=User.Role.STAFF,
            is_staff=True
        )

        customer1 = User.objects.create_user(
            email='customer1@example.com',
            password='customer123',
            first_name='Maria',
            last_name='Santos',
            role=User.Role.CUSTOMER
        )

        customer2 = User.objects.create_user(
            email='customer2@example.com',
            password='customer123',
            first_name='Juan',
            last_name='Dela Cruz',
            role=User.Role.CUSTOMER
        )

        customer3 = User.objects.create_user(
            email='customer3@example.com',
            password='customer123',
            first_name='Ana',
            last_name='Reyes',
            role=User.Role.CUSTOMER
        )

        self.stdout.write(f'  Created {User.objects.count()} users')
        return {
            'admin': admin,
            'staff': staff,
            'customers': [customer1, customer2, customer3]
        }

    def create_inventory(self):
        """Create demo inventory items."""
        items_data = [
            {'name': 'Hair Rebonding Solution', 'unit': 'ml', 'stock': 5000, 'threshold': 1000},
            {'name': 'Hair Coloring Cream', 'unit': 'ml', 'stock': 3000, 'threshold': 500},
            {'name': 'Shampoo', 'unit': 'ml', 'stock': 2000, 'threshold': 500},
            {'name': 'Conditioner', 'unit': 'ml', 'stock': 1800, 'threshold': 500},
            {'name': 'Hair Treatment Mask', 'unit': 'ml', 'stock': 1200, 'threshold': 300},
            {'name': 'Nail Polish', 'unit': 'pcs', 'stock': 150, 'threshold': 30},
            {'name': 'Nail Remover', 'unit': 'ml', 'stock': 500, 'threshold': 100},
            {'name': 'Cotton Balls', 'unit': 'pcs', 'stock': 500, 'threshold': 100},
            {'name': 'Facial Cleanser', 'unit': 'ml', 'stock': 800, 'threshold': 200},
            {'name': 'Face Mask', 'unit': 'pcs', 'stock': 80, 'threshold': 20},
            {'name': 'Massage Oil', 'unit': 'ml', 'stock': 600, 'threshold': 150},
            {'name': 'Wax Strips', 'unit': 'pcs', 'stock': 200, 'threshold': 50},
            {'name': 'Towels', 'unit': 'pcs', 'stock': 50, 'threshold': 10},
            {'name': 'Hair Clips', 'unit': 'pcs', 'stock': 100, 'threshold': 20},
            {'name': 'Gloves (pairs)', 'unit': 'pcs', 'stock': 200, 'threshold': 50},
        ]

        items = []
        for item_data in items_data:
            item = Item.objects.create(
                name=item_data['name'],
                description=f"Professional salon {item_data['name'].lower()}",
                unit=item_data['unit'],
                stock=Decimal(str(item_data['stock'])),
                threshold=Decimal(str(item_data['threshold'])),
                is_active=True
            )
            items.append(item)

        self.stdout.write(f'  Created {len(items)} inventory items')
        return items

    def create_services(self, items):
        """Create demo services with inventory requirements."""
        services_data = [
            {
                'name': 'Hair Rebond',
                'description': 'Professional hair rebonding treatment for straight, smooth hair',
                'price': 2500.00,
                'duration_minutes': 180,
                'items': {
                    'Hair Rebonding Solution': 200,
                    'Shampoo': 50,
                    'Conditioner': 50,
                    'Towels': 2,
                    'Hair Clips': 4,
                }
            },
            {
                'name': 'Hair Color',
                'description': 'Full hair coloring service with premium products',
                'price': 2000.00,
                'duration_minutes': 120,
                'items': {
                    'Hair Coloring Cream': 150,
                    'Shampoo': 40,
                    'Conditioner': 40,
                    'Gloves (pairs)': 2,
                    'Towels': 2,
                }
            },
            {
                'name': 'Hair Treatment',
                'description': 'Deep conditioning hair treatment',
                'price': 800.00,
                'duration_minutes': 60,
                'items': {
                    'Hair Treatment Mask': 100,
                    'Shampoo': 30,
                    'Towels': 1,
                }
            },
            {
                'name': 'Haircut',
                'description': 'Professional haircut and styling',
                'price': 300.00,
                'duration_minutes': 45,
                'items': {
                    'Shampoo': 20,
                    'Towels': 1,
                }
            },
            {
                'name': 'Manicure',
                'description': 'Complete manicure service',
                'price': 250.00,
                'duration_minutes': 45,
                'items': {
                    'Nail Polish': 1,
                    'Nail Remover': 10,
                    'Cotton Balls': 10,
                    'Towels': 1,
                }
            },
            {
                'name': 'Pedicure',
                'description': 'Complete pedicure service',
                'price': 350.00,
                'duration_minutes': 60,
                'items': {
                    'Nail Polish': 1,
                    'Nail Remover': 15,
                    'Cotton Balls': 15,
                    'Towels': 2,
                }
            },
            {
                'name': 'Facial Treatment',
                'description': 'Relaxing facial treatment',
                'price': 600.00,
                'duration_minutes': 75,
                'items': {
                    'Facial Cleanser': 30,
                    'Face Mask': 1,
                    'Cotton Balls': 20,
                    'Towels': 2,
                }
            },
            {
                'name': 'Body Massage',
                'description': 'Full body relaxation massage',
                'price': 800.00,
                'duration_minutes': 90,
                'items': {
                    'Massage Oil': 50,
                    'Towels': 3,
                }
            },
            {
                'name': 'Waxing Service',
                'description': 'Hair removal waxing service',
                'price': 400.00,
                'duration_minutes': 30,
                'items': {
                    'Wax Strips': 20,
                    'Cotton Balls': 10,
                    'Towels': 1,
                }
            },
        ]

        services = []
        items_by_name = {item.name: item for item in items}

        for service_data in services_data:
            service = Service.objects.create(
                name=service_data['name'],
                description=service_data['description'],
                price=Decimal(str(service_data['price'])),
                duration_minutes=service_data['duration_minutes'],
                is_active=True
            )

            # Link inventory items to service
            for item_name, qty in service_data['items'].items():
                if item_name in items_by_name:
                    ServiceItem.objects.create(
                        service=service,
                        item=items_by_name[item_name],
                        qty_per_service=Decimal(str(qty))
                    )

            services.append(service)

        self.stdout.write(f'  Created {len(services)} services')
        return services

    def create_appointment_settings(self):
        """Create appointment settings."""
        AppointmentSettings.objects.get_or_create(
            pk=1,
            defaults={
                'max_concurrent': 3,
                'booking_window_days': 30,
                'prevent_completion_on_insufficient_stock': True
            }
        )
        self.stdout.write('  Created appointment settings')

    def create_blocked_ranges(self):
        """Create blocked time ranges."""
        now = timezone.now()

        # Block next Sunday (example holiday)
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        next_sunday = now + timedelta(days=days_until_sunday)
        sunday_start = next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        sunday_end = sunday_start + timedelta(days=1)

        BlockedRange.objects.create(
            start_at=sunday_start,
            end_at=sunday_end,
            reason='Weekly day off'
        )

        self.stdout.write('  Created blocked ranges')

    def create_appointments(self, customers, services):
        """Create demo appointments."""
        now = timezone.now()
        appointments = []

        # Past completed appointments (last 30 days)
        for i in range(20):
            days_ago = random.randint(1, 30)
            start_time = now - timedelta(days=days_ago, hours=random.randint(9, 16))
            customer = random.choice(customers)
            service = random.choice(services)

            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                start_at=start_time,
                status=Appointment.Status.COMPLETED,
                payment_state=Appointment.PaymentState.PAID
            )
            appointments.append(appointment)

        # Upcoming appointments (next 14 days)
        for i in range(15):
            days_ahead = random.randint(1, 14)
            start_time = now + timedelta(days=days_ahead, hours=random.randint(9, 16))
            customer = random.choice(customers)
            service = random.choice(services)

            status_choices = [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
            payment_choices = [Appointment.PaymentState.UNPAID, Appointment.PaymentState.PAID]

            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                start_at=start_time,
                status=random.choice(status_choices),
                payment_state=random.choice(payment_choices)
            )
            appointments.append(appointment)

        # Some cancelled appointments
        for i in range(5):
            days_ago = random.randint(1, 15)
            start_time = now - timedelta(days=days_ago, hours=random.randint(9, 16))
            customer = random.choice(customers)
            service = random.choice(services)

            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                start_at=start_time,
                status=Appointment.Status.CANCELLED,
                payment_state=Appointment.PaymentState.UNPAID
            )
            appointments.append(appointment)

        self.stdout.write(f'  Created {len(appointments)} appointments')
        return appointments

    def create_payments(self, appointments):
        """Create payments for paid appointments."""
        from payments.views import generate_transaction_id

        payments = []
        for appointment in appointments:
            if appointment.payment_state == Appointment.PaymentState.PAID:
                method = random.choice([
                    Payment.Method.GCASH,
                    Payment.Method.PAYMAYA,
                    Payment.Method.ONSITE
                ])

                payment = Payment.objects.create(
                    appointment=appointment,
                    method=method,
                    amount=appointment.service.price,
                    status=Payment.Status.PAID,
                    txn_id=generate_transaction_id(),
                    notes=f'{method} payment successful'
                )
                payments.append(payment)

        self.stdout.write(f'  Created {len(payments)} payments')
        return payments

    def create_chatbot_rules(self):
        """Create chatbot rules."""
        rules_data = [
            {'keyword': 'hello', 'response': 'Hello! Welcome to Dreambook Salon. How can I help you today?', 'priority': 5},
            {'keyword': 'hi', 'response': 'Hi there! Welcome to Dreambook Salon. How may I assist you?', 'priority': 5},
            {'keyword': 'hours', 'response': 'We are open Monday to Saturday, 9:00 AM to 6:00 PM. Closed on Sundays.', 'priority': 10},
            {'keyword': 'location', 'response': 'We are located at 123 Main Street, Metro Manila. You can find us near the city center.', 'priority': 10},
            {'keyword': 'services', 'response': 'We offer hair services (rebond, color, treatment), nail services (manicure, pedicure), facial treatments, massage, and waxing. Visit our Services page for details!', 'priority': 10},
            {'keyword': 'price', 'response': 'Our prices vary by service. Haircuts start at ₱300, hair rebonding at ₱2,500, manicure at ₱250. Check our Services page for full pricing.', 'priority': 8},
            {'keyword': 'booking', 'response': 'To book an appointment, please log in to your account and visit the Appointments page. You can also call us directly!', 'priority': 10},
            {'keyword': 'book', 'response': 'To book an appointment, please log in to your account and visit the Appointments page. You can also call us directly!', 'priority': 10},
            {'keyword': 'appointment', 'response': 'You can book appointments through our website or by calling us. We require advance booking for most services.', 'priority': 8},
            {'keyword': 'cancel', 'response': 'To cancel an appointment, please log in to your account and go to My Appointments. You can cancel anytime before your scheduled time.', 'priority': 10},
            {'keyword': 'payment', 'response': 'We accept GCash, PayMaya, and cash payments onsite. Online payments can be made through our website.', 'priority': 8},
            {'keyword': 'contact', 'response': 'You can reach us at contact@dreambook.com or call us at (02) 1234-5678 during business hours.', 'priority': 10},
            {'keyword': 'email', 'response': 'You can email us at contact@dreambook.com. We typically respond within 24 hours.', 'priority': 8},
            {'keyword': 'phone', 'response': 'You can call us at (02) 1234-5678 during business hours (Mon-Sat, 9 AM - 6 PM).', 'priority': 8},
            {'keyword': 'rebond', 'response': 'Our hair rebonding service costs ₱2,500 and takes about 3 hours. It includes professional treatment for straight, smooth hair.', 'priority': 9},
            {'keyword': 'color', 'response': 'Hair coloring service costs ₱2,000 and takes about 2 hours. We use premium professional products.', 'priority': 9},
            {'keyword': 'haircut', 'response': 'Professional haircut and styling costs ₱300 and takes about 45 minutes.', 'priority': 9},
            {'keyword': 'manicure', 'response': 'Our manicure service costs ₱250 and takes about 45 minutes. Includes nail polish application.', 'priority': 9},
            {'keyword': 'pedicure', 'response': 'Our pedicure service costs ₱350 and takes about 1 hour. Includes nail polish application.', 'priority': 9},
            {'keyword': 'facial', 'response': 'Relaxing facial treatment costs ₱600 and takes about 75 minutes. Perfect for skin rejuvenation!', 'priority': 9},
            {'keyword': 'massage', 'response': 'Full body massage costs ₱800 and takes about 90 minutes. Very relaxing!', 'priority': 9},
            {'keyword': 'thank', 'response': 'You\'re welcome! Is there anything else I can help you with?', 'priority': 5},
            {'keyword': 'thanks', 'response': 'You\'re welcome! Feel free to ask if you need anything else.', 'priority': 5},
        ]

        rules = []
        for rule_data in rules_data:
            rule = Rule.objects.create(
                keyword=rule_data['keyword'],
                response=rule_data['response'],
                priority=rule_data['priority'],
                is_active=True
            )
            rules.append(rule)

        self.stdout.write(f'  Created {len(rules)} chatbot rules')
        return rules
