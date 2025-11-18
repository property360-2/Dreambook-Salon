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
    help = "Seed database with demo data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        with transaction.atomic():
            # Create users
            self.stdout.write("Creating users...")
            users = self.create_users()

            # Create inventory items
            self.stdout.write("Creating inventory items...")
            items = self.create_inventory()

            # Create services
            self.stdout.write("Creating services...")
            services = self.create_services(items)

            # Create appointment settings
            self.stdout.write("Creating appointment settings...")
            self.create_appointment_settings()

            # Create blocked ranges
            self.stdout.write("Creating blocked ranges...")
            self.create_blocked_ranges()

            # Create appointments
            self.stdout.write("Creating appointments...")
            appointments = self.create_appointments(users["customers"], services)

            # Create payments
            self.stdout.write("Creating payments...")
            self.create_payments(appointments)

            # Create chatbot rules
            self.stdout.write("Creating chatbot rules...")
            self.create_chatbot_rules()

        self.stdout.write(
            self.style.SUCCESS("Database seeding completed successfully!")
        )

    def clear_data(self):
        """Clear existing demo data."""
        Payment.objects.all().delete()
        Appointment.objects.all().delete()
        BlockedRange.objects.all().delete()
        ServiceItem.objects.all().delete()
        Service.objects.all().delete()
        Item.objects.all().delete()
        Rule.objects.all().delete()
        User.objects.filter(
            email__in=[
                "admin@dreambook.com",
                "staff@dreambook.com",
                "customer1@example.com",
                "customer2@example.com",
                "customer3@example.com",
            ]
        ).delete()

    def create_users(self):
        """Create demo users."""
        admin = User.objects.create_user(
            email="admin@dreambook.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            role=User.Roles.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        staff = User.objects.create_user(
            email="staff@dreambook.com",
            password="staff123",
            first_name="Staff",
            last_name="Member",
            role=User.Roles.STAFF,
            is_staff=True,
        )

        customer1 = User.objects.create_user(
            email="customer1@example.com",
            password="customer123",
            first_name="Maria",
            last_name="Santos",
            role=User.Roles.CUSTOMER,
        )

        customer2 = User.objects.create_user(
            email="customer2@example.com",
            password="customer123",
            first_name="Juan",
            last_name="Dela Cruz",
            role=User.Roles.CUSTOMER,
        )

        customer3 = User.objects.create_user(
            email="customer3@example.com",
            password="customer123",
            first_name="Ana",
            last_name="Reyes",
            role=User.Roles.CUSTOMER,
        )

        self.stdout.write(f"  Created {User.objects.count()} users")
        return {
            "admin": admin,
            "staff": staff,
            "customers": [customer1, customer2, customer3],
        }

    def create_inventory(self):
        """Create demo inventory items."""
        items_data = [
            {
                "name": "Hair Rebonding Solution",
                "unit": "ml",
                "stock": 5000,
                "threshold": 1000,
            },
            {
                "name": "Hair Coloring Cream",
                "unit": "ml",
                "stock": 3000,
                "threshold": 500,
            },
            {"name": "Shampoo", "unit": "ml", "stock": 2000, "threshold": 500},
            {"name": "Conditioner", "unit": "ml", "stock": 1800, "threshold": 500},
            {
                "name": "Hair Treatment Mask",
                "unit": "ml",
                "stock": 1200,
                "threshold": 300,
            },
            {"name": "Nail Polish", "unit": "pcs", "stock": 150, "threshold": 30},
            {"name": "Nail Remover", "unit": "ml", "stock": 500, "threshold": 100},
            {"name": "Cotton Balls", "unit": "pcs", "stock": 500, "threshold": 100},
            {"name": "Facial Cleanser", "unit": "ml", "stock": 800, "threshold": 200},
            {"name": "Face Mask", "unit": "pcs", "stock": 80, "threshold": 20},
            {"name": "Massage Oil", "unit": "ml", "stock": 600, "threshold": 150},
            {"name": "Wax Strips", "unit": "pcs", "stock": 200, "threshold": 50},
            {"name": "Towels", "unit": "pcs", "stock": 50, "threshold": 10},
            {"name": "Hair Clips", "unit": "pcs", "stock": 100, "threshold": 20},
            {"name": "Gloves (pairs)", "unit": "pcs", "stock": 200, "threshold": 50},
        ]

        items = []
        for item_data in items_data:
            item = Item.objects.create(
                name=item_data["name"],
                description=f"Professional salon {item_data['name'].lower()}",
                unit=item_data["unit"],
                stock=Decimal(str(item_data["stock"])),
                threshold=Decimal(str(item_data["threshold"])),
                is_active=True,
            )
            items.append(item)

        self.stdout.write(f"  Created {len(items)} inventory items")
        return items

    def create_services(self, items):
        """Create demo services with inventory requirements."""
        services_data = [
            # HAIR SERVICES
            {
                "name": "Haircut",
                "description": "Professional haircut and styling - includes wash, cut, and style",
                "price": 100.00,
                "duration_minutes": 45,
                "items": {
                    "Shampoo": 20,
                    "Conditioner": 10,
                    "Towels": 1,
                    "Hair Clips": 2,
                },
            },
            {
                "name": "Hair Spa",
                "description": "Relaxing hair spa treatment with premium conditioning mask",
                "price": 500.00,
                "duration_minutes": 75,
                "items": {
                    "Hair Treatment Mask": 80,
                    "Shampoo": 40,
                    "Conditioner": 40,
                    "Massage Oil": 30,
                    "Towels": 2,
                },
            },
            {
                "name": "Hair Color",
                "description": "Full hair coloring service with premium hair dye (starts at ₱700)",
                "price": 700.00,
                "duration_minutes": 120,
                "items": {
                    "Hair Coloring Cream": 150,
                    "Shampoo": 40,
                    "Conditioner": 40,
                    "Gloves (pairs)": 2,
                    "Towels": 2,
                },
            },
            {
                "name": "Hair & Make-Up",
                "description": "Complete hair styling with professional make-up for events",
                "price": 1000.00,
                "duration_minutes": 150,
                "items": {
                    "Hair Treatment Mask": 50,
                    "Shampoo": 40,
                    "Conditioner": 30,
                    "Facial Cleanser": 30,
                    "Hair Clips": 6,
                    "Towels": 3,
                    "Cotton Balls": 20,
                },
            },
            {
                "name": "Keratin Treatment",
                "description": "Professional keratin treatment for smooth, shiny, manageable hair",
                "price": 1000.00,
                "duration_minutes": 180,
                "items": {
                    "Hair Rebonding Solution": 200,
                    "Hair Treatment Mask": 100,
                    "Shampoo": 50,
                    "Conditioner": 50,
                    "Towels": 3,
                    "Hair Clips": 4,
                },
            },
            {
                "name": "Botox Hair Treatment",
                "description": "Advanced botox hair treatment for damaged and frizzy hair",
                "price": 1200.00,
                "duration_minutes": 120,
                "items": {
                    "Hair Treatment Mask": 120,
                    "Hair Rebonding Solution": 100,
                    "Shampoo": 45,
                    "Conditioner": 45,
                    "Towels": 2,
                },
            },
            {
                "name": "Brazilian Hair Treatment",
                "description": "Brazilian smoothing treatment for frizz control and shine",
                "price": 1500.00,
                "duration_minutes": 150,
                "items": {
                    "Hair Rebonding Solution": 250,
                    "Hair Treatment Mask": 100,
                    "Shampoo": 50,
                    "Conditioner": 50,
                    "Towels": 3,
                    "Hair Clips": 5,
                },
            },
            {
                "name": "Hair Rebond",
                "description": "Professional hair rebonding treatment for permanent smoothness (starts at ₱1,500)",
                "price": 1500.00,
                "duration_minutes": 180,
                "items": {
                    "Hair Rebonding Solution": 200,
                    "Shampoo": 50,
                    "Conditioner": 50,
                    "Towels": 2,
                    "Hair Clips": 4,
                },
            },
            {
                "name": "Collagen Treatment",
                "description": "Collagen-infused hair treatment for strength and elasticity (starts at ₱2,000)",
                "price": 2000.00,
                "duration_minutes": 120,
                "items": {
                    "Hair Treatment Mask": 150,
                    "Hair Rebonding Solution": 80,
                    "Shampoo": 40,
                    "Conditioner": 40,
                    "Towels": 2,
                },
            },
            # NAIL SERVICES
            {
                "name": "Manicure",
                "description": "Complete manicure service with nail care and polish",
                "price": 250.00,
                "duration_minutes": 45,
                "items": {
                    "Nail Polish": 1,
                    "Nail Remover": 10,
                    "Cotton Balls": 10,
                    "Towels": 1,
                },
            },
            {
                "name": "Pedicure",
                "description": "Complete pedicure service with foot care and polish",
                "price": 350.00,
                "duration_minutes": 60,
                "items": {
                    "Nail Polish": 1,
                    "Nail Remover": 15,
                    "Cotton Balls": 15,
                    "Towels": 2,
                },
            },
            # BEAUTY & WELLNESS
            {
                "name": "Facial Treatment",
                "description": "Relaxing facial treatment for skin rejuvenation and glow",
                "price": 600.00,
                "duration_minutes": 75,
                "items": {
                    "Facial Cleanser": 30,
                    "Face Mask": 1,
                    "Cotton Balls": 20,
                    "Towels": 2,
                },
            },
            {
                "name": "Body Massage",
                "description": "Full body relaxation massage for stress relief",
                "price": 800.00,
                "duration_minutes": 90,
                "items": {
                    "Massage Oil": 50,
                    "Towels": 3,
                },
            },
            {
                "name": "Waxing Service",
                "description": "Professional hair removal waxing service",
                "price": 400.00,
                "duration_minutes": 30,
                "items": {
                    "Wax Strips": 20,
                    "Cotton Balls": 10,
                    "Towels": 1,
                },
            },
        ]

        services = []
        items_by_name = {item.name: item for item in items}

        for service_data in services_data:
            service = Service.objects.create(
                name=service_data["name"],
                description=service_data["description"],
                price=Decimal(str(service_data["price"])),
                duration_minutes=service_data["duration_minutes"],
                is_active=True,
            )

            # Link inventory items to service
            for item_name, qty in service_data["items"].items():
                if item_name in items_by_name:
                    ServiceItem.objects.create(
                        service=service,
                        item=items_by_name[item_name],
                        qty_per_service=Decimal(str(qty)),
                    )

            services.append(service)

        self.stdout.write(f"  Created {len(services)} services")
        return services

    def create_appointment_settings(self):
        """Create appointment settings."""
        AppointmentSettings.objects.get_or_create(
            pk=1,
            defaults={
                "max_concurrent": 3,
                "booking_window_days": 30,
                "prevent_completion_on_insufficient_stock": True,
            },
        )
        self.stdout.write("  Created appointment settings")

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
            start_at=sunday_start, end_at=sunday_end, reason="Weekly day off"
        )

        self.stdout.write("  Created blocked ranges")

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
                status="completed",
                payment_state="paid",
            )
            appointments.append(appointment)

        # Upcoming appointments (next 14 days)
        for i in range(15):
            days_ahead = random.randint(1, 14)
            start_time = now + timedelta(days=days_ahead, hours=random.randint(9, 16))
            customer = random.choice(customers)
            service = random.choice(services)

            status_choices = ["pending", "confirmed"]
            payment_choices = ["unpaid", "paid"]

            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                start_at=start_time,
                status=random.choice(status_choices),
                payment_state=random.choice(payment_choices),
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
                status="cancelled",
                payment_state="unpaid",
            )
            appointments.append(appointment)

        self.stdout.write(f"  Created {len(appointments)} appointments")
        return appointments

    def create_payments(self, appointments):
        """Create payments for paid appointments."""
        import uuid

        payments = []
        for appointment in appointments:
            if appointment.payment_state == "paid":
                method = random.choice(["gcash", "paymaya", "onsite"])

                payment = Payment.objects.create(
                    appointment=appointment,
                    method=method,
                    amount=appointment.service.price,
                    status="paid",
                    txn_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                    notes=f"{method.upper()} payment successful",
                )
                payments.append(payment)

        self.stdout.write(f"  Created {len(payments)} payments")
        return payments

    def create_chatbot_rules(self):
        """Create comprehensive chatbot rules."""
        rules_data = [
            # GREETINGS
            {
                "keyword": "hello",
                "response": "Hello! Welcome to Dreambook Salon. How can I help you today?",
                "priority": 5,
            },
            {
                "keyword": "hi",
                "response": "Hi there! Welcome to Dreambook Salon. How may I assist you?",
                "priority": 5,
            },
            {
                "keyword": "hey",
                "response": "Hey! Welcome to Dreambook Salon. What can I do for you?",
                "priority": 5,
            },
            {
                "keyword": "greetings",
                "response": "Greetings! Welcome to our salon. Feel free to ask me anything!",
                "priority": 5,
            },
            {
                "keyword": "good morning",
                "response": "Good morning! Welcome to Dreambook Salon. How can I assist you?",
                "priority": 5,
            },
            {
                "keyword": "good afternoon",
                "response": "Good afternoon! Welcome to Dreambook Salon. What can I help you with?",
                "priority": 5,
            },
            # BUSINESS HOURS
            {
                "keyword": "hours",
                "response": "We are open Monday to Saturday, 9:00 AM to 6:00 PM. Closed on Sundays.",
                "priority": 10,
            },
            {
                "keyword": "open",
                "response": "We are open Monday to Saturday, 9:00 AM to 6:00 PM.",
                "priority": 10,
            },
            {
                "keyword": "close",
                "response": "We close at 6:00 PM on weekdays. We are closed on Sundays.",
                "priority": 10,
            },
            {
                "keyword": "operating hours",
                "response": "Our operating hours are Mon-Sat 9 AM - 6 PM. We're closed on Sundays.",
                "priority": 10,
            },
            {
                "keyword": "what time",
                "response": "We are open 9 AM to 6 PM, Monday through Saturday.",
                "priority": 8,
            },
            # LOCATION & DIRECTIONS
            {
                "keyword": "location",
                "response": "We are located at 123 Main Street, Metro Manila. You can find us near the city center.",
                "priority": 10,
            },
            {
                "keyword": "address",
                "response": "Our address is 123 Main Street, Metro Manila. We're easy to find!",
                "priority": 10,
            },
            {
                "keyword": "where",
                "response": "You can find us at 123 Main Street, Metro Manila, near the city center.",
                "priority": 10,
            },
            {
                "keyword": "directions",
                "response": "We're located at 123 Main Street, Metro Manila. GPS coordinates available on our contact page.",
                "priority": 9,
            },
            {
                "keyword": "near",
                "response": "We are conveniently located near the city center at 123 Main Street.",
                "priority": 8,
            },
            # SERVICES OVERVIEW
            {
                "keyword": "services",
                "response": "We offer: Hair Services (Haircut, Hair Spa, Hair Color, Hair & Make-Up, Keratin, Botox, Brazilian, Rebond, Collagen), Nail Services (Manicure, Pedicure), and Beauty Services (Facial, Massage, Waxing). Visit our Services page for details!",
                "priority": 10,
            },
            {
                "keyword": "service",
                "response": "We provide a wide range of salon services. Check our Services page to see all options!",
                "priority": 8,
            },
            {
                "keyword": "what do you offer",
                "response": "We offer professional hair treatments, nail care, facials, massage, and more. Visit our Services page!",
                "priority": 8,
            },
            # HAIR SERVICES - GENERAL
            {
                "keyword": "hair",
                "response": "We offer many hair services: Haircut (₱100), Hair Spa (₱500), Hair Color (₱700+), Hair & Make-Up (₱1,000), Keratin (₱1,000), Botox (₱1,200), Brazilian (₱1,500), Rebond (₱1,500), and Collagen (₱2,000). Which interests you?",
                "priority": 9,
            },
            {
                "keyword": "hair treatment",
                "response": "We offer multiple hair treatments: Hair Spa, Keratin, Botox, Brazilian, Rebond, and Collagen. All designed for different hair needs!",
                "priority": 9,
            },
            # SPECIFIC HAIR SERVICES
            {
                "keyword": "haircut",
                "response": "Professional haircut and styling costs ₱100 and takes about 45 minutes. Includes wash, cut, and style!",
                "priority": 9,
            },
            {
                "keyword": "hair spa",
                "response": "Hair Spa treatment costs ₱500 and takes about 75 minutes. A relaxing treatment with premium conditioning mask.",
                "priority": 9,
            },
            {
                "keyword": "color",
                "response": "Hair coloring service starts at ₱700 and takes about 2 hours. We use premium professional products for the best results.",
                "priority": 9,
            },
            {
                "keyword": "hair color",
                "response": "Hair Color service costs ₱700+ and takes 2 hours. Professional color application with quality dye products.",
                "priority": 9,
            },
            {
                "keyword": "hair makeup",
                "response": "Hair & Make-Up service costs ₱1,000 and takes 2.5 hours. Perfect for events with complete styling and makeup!",
                "priority": 9,
            },
            {
                "keyword": "keratin",
                "response": "Keratin treatment costs ₱1,000 and takes 3 hours. Gives your hair smoothness, shine, and manageability.",
                "priority": 9,
            },
            {
                "keyword": "botox hair",
                "response": "Botox Hair Treatment costs ₱1,200 and takes 2 hours. Advanced treatment for damaged and frizzy hair.",
                "priority": 9,
            },
            {
                "keyword": "brazilian",
                "response": "Brazilian Hair Treatment costs ₱1,500 and takes 2.5 hours. Perfect for frizz control and adding shine to your hair.",
                "priority": 9,
            },
            {
                "keyword": "rebond",
                "response": "Hair Rebond treatment costs ₱1,500 and takes 3 hours. Permanent smoothing treatment for straight, smooth hair.",
                "priority": 9,
            },
            {
                "keyword": "collagen",
                "response": "Collagen Treatment costs ₱2,000 and takes 2 hours. Infuses your hair with strength and elasticity.",
                "priority": 9,
            },
            {
                "keyword": "smoothing",
                "response": "We offer Hair Rebond (₱1,500) and Brazilian Treatment (₱1,500) for hair smoothing. Both are permanent solutions!",
                "priority": 9,
            },
            {
                "keyword": "frizz",
                "response": "For frizz control, we recommend our Brazilian Treatment (₱1,500) or Botox Hair Treatment (₱1,200).",
                "priority": 9,
            },
            # NAIL SERVICES
            {
                "keyword": "nail",
                "response": "We offer Manicure (₱250, 45 min) and Pedicure (₱350, 60 min). Both include nail care and polish application!",
                "priority": 9,
            },
            {
                "keyword": "manicure",
                "response": "Manicure service costs ₱250 and takes about 45 minutes. Includes complete nail care and polish application.",
                "priority": 9,
            },
            {
                "keyword": "pedicure",
                "response": "Pedicure service costs ₱350 and takes about 60 minutes. Includes foot care and nail polish application.",
                "priority": 9,
            },
            {
                "keyword": "nails",
                "response": "We provide professional manicure and pedicure services. Manicure: ₱250 (45 min), Pedicure: ₱350 (60 min).",
                "priority": 9,
            },
            # BEAUTY & WELLNESS SERVICES
            {
                "keyword": "facial",
                "response": "Facial Treatment costs ₱600 and takes 75 minutes. Perfect for skin rejuvenation and a healthy glow!",
                "priority": 9,
            },
            {
                "keyword": "massage",
                "response": "Full Body Massage costs ₱800 and takes 90 minutes. Very relaxing and perfect for stress relief!",
                "priority": 9,
            },
            {
                "keyword": "wax",
                "response": "Waxing Service costs ₱400 and takes 30 minutes. Professional hair removal service.",
                "priority": 9,
            },
            {
                "keyword": "relax",
                "response": "For relaxation, try our Body Massage (₱800, 90 min) or Hair Spa (₱500, 75 min)!",
                "priority": 8,
            },
            # PRICING
            {
                "keyword": "price",
                "response": "Our services range from ₱100 (Haircut) to ₱2,000 (Collagen). Check our Services page for complete pricing!",
                "priority": 8,
            },
            {
                "keyword": "cost",
                "response": "Pricing varies by service. Haircuts start at ₱100, hair treatments from ₱500-₱2,000, nails at ₱250-₱350.",
                "priority": 8,
            },
            {
                "keyword": "how much",
                "response": "Prices vary by service. Haircut: ₱100, Hair Spa: ₱500, Color: ₱700+, Keratin: ₱1,000, Botox: ₱1,200, Brazilian/Rebond: ₱1,500, Collagen: ₱2,000.",
                "priority": 9,
            },
            {
                "keyword": "expensive",
                "response": "Our prices are competitive for professional salon services. We use premium products and skilled professionals!",
                "priority": 7,
            },
            {
                "keyword": "discount",
                "response": "For special promotions and discounts, please contact us at contact@dreambook.com or call (02) 1234-5678.",
                "priority": 8,
            },
            # BOOKING & APPOINTMENTS
            {
                "keyword": "booking",
                "response": "To book an appointment, please log in to your account and visit the Appointments page. You can also call us at (02) 1234-5678!",
                "priority": 10,
            },
            {
                "keyword": "book",
                "response": "You can book through our website by logging in and visiting the Appointments page, or call us directly!",
                "priority": 10,
            },
            {
                "keyword": "appointment",
                "response": "Book appointments through our website or call us. We recommend booking in advance for popular services!",
                "priority": 8,
            },
            {
                "keyword": "reserve",
                "response": "To reserve your spot, use our online booking system on the Appointments page or call us!",
                "priority": 8,
            },
            {
                "keyword": "schedule",
                "response": "You can schedule appointments online through our website or contact us at (02) 1234-5678.",
                "priority": 8,
            },
            {
                "keyword": "how to book",
                "response": "Log in to your account, go to the Appointments page, select your service, date, and time. Simple as that!",
                "priority": 9,
            },
            {
                "keyword": "advance booking",
                "response": "We accept advance bookings up to 30 days ahead. We recommend booking early for popular services!",
                "priority": 8,
            },
            # CANCELLATION & RESCHEDULING
            {
                "keyword": "cancel",
                "response": "To cancel an appointment, log in to your account, go to My Appointments, and cancel. You can cancel anytime before your scheduled time.",
                "priority": 10,
            },
            {
                "keyword": "cancellation",
                "response": "You can cancel appointments through your account on the My Appointments page. No fees if cancelled before your appointment time.",
                "priority": 9,
            },
            {
                "keyword": "reschedule",
                "response": "To reschedule, cancel your current appointment and book a new one at your preferred time!",
                "priority": 8,
            },
            {
                "keyword": "change appointment",
                "response": "You can modify your appointment by cancelling and rebooking through your account.",
                "priority": 8,
            },
            {
                "keyword": "postpone",
                "response": "To postpone your appointment, cancel it and book a new date that works better for you!",
                "priority": 7,
            },
            # PAYMENT & METHODS
            {
                "keyword": "payment",
                "response": "We accept GCash, PayMaya, and cash payments onsite. Online payments can be made through our website during booking!",
                "priority": 8,
            },
            {
                "keyword": "pay",
                "response": "Payment methods: GCash, PayMaya (online), or cash at the salon. Choose what works best for you!",
                "priority": 8,
            },
            {
                "keyword": "gcash",
                "response": "Yes, we accept GCash payments online. It's quick, secure, and convenient!",
                "priority": 8,
            },
            {
                "keyword": "paymaya",
                "response": "Yes, we accept PayMaya for online payments. It's one of our convenient payment options!",
                "priority": 8,
            },
            {
                "keyword": "cash",
                "response": "Of course! We accept cash payments when you visit our salon.",
                "priority": 7,
            },
            {
                "keyword": "credit card",
                "response": "We primarily accept GCash and PayMaya online, or cash at the salon. Please contact us for other card options!",
                "priority": 7,
            },
            # CONTACT INFORMATION
            {
                "keyword": "contact",
                "response": "Email: contact@dreambook.com | Phone: (02) 1234-5678 | Address: 123 Main Street, Metro Manila",
                "priority": 10,
            },
            {
                "keyword": "email",
                "response": "You can email us at contact@dreambook.com. We typically respond within 24 hours.",
                "priority": 8,
            },
            {
                "keyword": "phone",
                "response": "Call us at (02) 1234-5678 during business hours (Mon-Sat, 9 AM - 6 PM).",
                "priority": 8,
            },
            {
                "keyword": "call",
                "response": "Call us at (02) 1234-5678. Our team is available Mon-Sat, 9 AM - 6 PM.",
                "priority": 8,
            },
            {
                "keyword": "reach out",
                "response": "You can reach us via email (contact@dreambook.com) or phone ((02) 1234-5678) anytime!",
                "priority": 8,
            },
            # CUSTOMER SUPPORT
            {
                "keyword": "help",
                "response": "I'm here to help! Ask me about services, pricing, booking, or anything else about Dreambook Salon!",
                "priority": 5,
            },
            {
                "keyword": "support",
                "response": "Need support? Contact us at contact@dreambook.com or (02) 1234-5678 for personalized assistance!",
                "priority": 8,
            },
            {
                "keyword": "assistance",
                "response": "We're happy to assist! Feel free to ask about our services, booking, or any other questions!",
                "priority": 7,
            },
            {
                "keyword": "problem",
                "response": "Sorry to hear that! Please contact our team at (02) 1234-5678 or email contact@dreambook.com for immediate help.",
                "priority": 9,
            },
            {
                "keyword": "issue",
                "response": "We're sorry! Please reach out to our support team at contact@dreambook.com or (02) 1234-5678.",
                "priority": 9,
            },
            # QUALIFICATIONS & EXPERTISE
            {
                "keyword": "professional",
                "response": "Yes! Our team consists of certified and experienced salon professionals with years of expertise.",
                "priority": 8,
            },
            {
                "keyword": "skilled",
                "response": "Absolutely! Our stylists are highly skilled and trained in the latest salon techniques.",
                "priority": 8,
            },
            {
                "keyword": "experience",
                "response": "Our team has extensive experience in hair care, beauty, and wellness services.",
                "priority": 8,
            },
            {
                "keyword": "certified",
                "response": "Our staff are certified professionals with proper training in all salon services.",
                "priority": 8,
            },
            # PRODUCTS & QUALITY
            {
                "keyword": "product",
                "response": "We use premium, professional-grade products from trusted brands for the best results!",
                "priority": 8,
            },
            {
                "keyword": "quality",
                "response": "Quality is our priority! We use the best products and techniques for excellent results every time.",
                "priority": 8,
            },
            {
                "keyword": "brand",
                "response": "We use trusted, professional-grade brands known for quality and reliability.",
                "priority": 8,
            },
            # DURATION & TIME
            {
                "keyword": "how long",
                "response": "Service duration varies: Haircut (45 min), Hair Spa (75 min), Color (120 min), Keratin (180 min), etc. Ask about specific services!",
                "priority": 8,
            },
            {
                "keyword": "duration",
                "response": "Duration varies by service. Haircuts take 45 minutes, hair treatments 60-180 minutes. Check our Services page!",
                "priority": 8,
            },
            {
                "keyword": "time",
                "response": "Service times vary from 30 minutes (Waxing) to 3 hours (Hair Rebond, Keratin). Visit Services page for details!",
                "priority": 8,
            },
            # SPECIAL OCCASIONS
            {
                "keyword": "event",
                "response": "For special events, try our Hair & Make-Up service (₱1,000, 150 min) for complete styling!",
                "priority": 8,
            },
            {
                "keyword": "wedding",
                "response": "Perfect for weddings! Our Hair & Make-Up service (₱1,000) provides complete styling for your special day!",
                "priority": 8,
            },
            {
                "keyword": "party",
                "response": "Prepare for your party with our Hair & Make-Up service (₱1,000) for stunning results!",
                "priority": 8,
            },
            {
                "keyword": "special event",
                "response": "For special events, we recommend our Hair & Make-Up service for complete styling!",
                "priority": 8,
            },
            # FREQUENTLY ASKED
            {
                "keyword": "faq",
                "response": "Common questions: How to book? (Go to Appointments page), Payment methods? (GCash, PayMaya, Cash), Hours? (Mon-Sat 9AM-6PM). Ask anything!",
                "priority": 8,
            },
            {
                "keyword": "question",
                "response": "Feel free to ask! I'm here to answer any questions about our services, booking, or anything else!",
                "priority": 6,
            },
            # THANK YOU & FAREWELL
            {
                "keyword": "thank",
                "response": "You're welcome! Is there anything else I can help you with?",
                "priority": 5,
            },
            {
                "keyword": "thanks",
                "response": "You're welcome! Feel free to ask if you need anything else. Looking forward to seeing you!",
                "priority": 5,
            },
            {
                "keyword": "thank you",
                "response": "You're very welcome! We appreciate your interest. See you soon!",
                "priority": 5,
            },
            {
                "keyword": "goodbye",
                "response": "Thank you for visiting Dreambook Salon! See you soon!",
                "priority": 5,
            },
            {
                "keyword": "bye",
                "response": "Goodbye! Book your appointment soon. We look forward to seeing you!",
                "priority": 5,
            },
            {
                "keyword": "see you",
                "response": "See you soon! Don't forget to book your appointment!",
                "priority": 5,
            },
            # FEEDBACK & REVIEWS
            {
                "keyword": "review",
                "response": "We'd love to hear your feedback! Contact us or share your experience with us!",
                "priority": 6,
            },
            {
                "keyword": "feedback",
                "response": "Your feedback is important to us! Please share your thoughts at contact@dreambook.com.",
                "priority": 6,
            },
            {
                "keyword": "rating",
                "response": "We appreciate your interest! Visit us and share your experience after your service!",
                "priority": 6,
            },
            # ONLINE PRESENCE
            {
                "keyword": "website",
                "response": "Our website has all the information you need about services, booking, and contact details!",
                "priority": 7,
            },
            {
                "keyword": "social media",
                "response": "Follow us for updates! Contact us at contact@dreambook.com for social media links.",
                "priority": 6,
            },
            {
                "keyword": "online",
                "response": "Yes! You can book appointments and manage your account online through our website.",
                "priority": 8,
            },
            # MISCELLANEOUS
            {
                "keyword": "what",
                "response": "I'm here to help with any questions about Dreambook Salon's services and booking!",
                "priority": 4,
            },
            {
                "keyword": "who",
                "response": "I'm the Dreambook Salon chatbot, here to assist you with services, booking, and questions!",
                "priority": 5,
            },
            {
                "keyword": "why",
                "response": "We exist to provide top-quality salon services to our valued customers!",
                "priority": 5,
            },
            {
                "keyword": "when",
                "response": "We're open Mon-Sat, 9 AM - 6 PM. Closed on Sundays. Book anytime up to 30 days ahead!",
                "priority": 7,
            },
        ]

        rules = []
        for rule_data in rules_data:
            rule = Rule.objects.create(
                keyword=rule_data["keyword"],
                response=rule_data["response"],
                priority=rule_data["priority"],
                is_active=True,
            )
            rules.append(rule)

        self.stdout.write(f"  Created {len(rules)} chatbot rules")
        return rules
