import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Count, Sum, Max
from core.models import User
from services.models import Service
from inventory.models import Item
from appointments.models import Appointment
from payments.models import Payment

class Command(BaseCommand):
    help = 'Generate BI CSV reports from current database data'

    def handle(self, *args, **options):
        # Create bi-reports directory if it doesn't exist
        reports_dir = os.path.join(settings.BASE_DIR, 'bi-reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {reports_dir}'))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stdout.write(f"Generating reports at {reports_dir}...")

        # 1. Appointments Report
        self.generate_appointments_report(reports_dir)

        # 2. Payments Report
        self.generate_payments_report(reports_dir)

        # 3. Inventory Report
        self.generate_inventory_report(reports_dir)

        # 4. Services Report
        self.generate_services_report(reports_dir)

        # 5. Customers Report
        self.generate_customers_report(reports_dir)

        self.stdout.write(self.style.SUCCESS(f'Successfully generated all BI reports in {reports_dir}'))

    def generate_appointments_report(self, output_dir):
        filepath = os.path.join(output_dir, 'appointments.csv')
        queryset = Appointment.objects.select_related('customer', 'service').all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Appointment ID', 'Customer Email', 'Customer Name', 'Service Name', 
                'Price', 'Start Time', 'End Time', 'Status', 'Payment State', 
                'Created At', 'Cancelled At', 'Cancellation Reason'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for appt in queryset:
                writer.writerow({
                    'Appointment ID': appt.id,
                    'Customer Email': appt.customer.email,
                    'Customer Name': f"{appt.customer.first_name} {appt.customer.last_name}",
                    'Service Name': appt.service.name,
                    'Price': appt.service.price,
                    'Start Time': appt.start_at.isoformat(),
                    'End Time': appt.end_at.isoformat() if appt.end_at else '',
                    'Status': appt.status,
                    'Payment State': appt.payment_state,
                    'Created At': appt.created_at.isoformat(),
                    'Cancelled At': appt.cancelled_at.isoformat() if appt.cancelled_at else '',
                    'Cancellation Reason': appt.cancellation_reason
                })
        
        self.stdout.write(f"  - Generated appointments.csv ({queryset.count()} records)")

    def generate_payments_report(self, output_dir):
        filepath = os.path.join(output_dir, 'payments.csv')
        queryset = Payment.objects.select_related('appointment', 'appointment__customer').all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Payment ID', 'Transaction ID', 'Method', 'Amount', 'Status', 
                'Payment Type', 'Appointment ID', 'Customer Email', 'Date', 'Notes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for payment in queryset:
                writer.writerow({
                    'Payment ID': payment.id,
                    'Transaction ID': payment.txn_id,
                    'Method': payment.method,
                    'Amount': payment.amount,
                    'Status': payment.status,
                    'Payment Type': payment.payment_type,
                    'Appointment ID': payment.appointment.id,
                    'Customer Email': payment.appointment.customer.email,
                    'Date': payment.created_at.isoformat(),
                    'Notes': payment.notes
                })
                
        self.stdout.write(f"  - Generated payments.csv ({queryset.count()} records)")

    def generate_inventory_report(self, output_dir):
        filepath = os.path.join(output_dir, 'inventory.csv')
        queryset = Item.objects.all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Item ID', 'Name', 'Category', 'Stock', 'Unit', 
                'Threshold', 'Status', 'Expiry Date', 'Is Active'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in queryset:
                writer.writerow({
                    'Item ID': item.id,
                    'Name': item.name,
                    'Category': item.category,
                    'Stock': item.stock,
                    'Unit': item.unit,
                    'Threshold': item.threshold,
                    'Status': item.stock_status,  # Using the property method
                    'Expiry Date': item.expiry_date.isoformat() if item.expiry_date else '',
                    'Is Active': item.is_active
                })
                
        self.stdout.write(f"  - Generated inventory.csv ({queryset.count()} records)")

    def generate_services_report(self, output_dir):
        filepath = os.path.join(output_dir, 'services.csv')
        # Annotate with booking count and total revenue
        queryset = Service.objects.annotate(
            total_bookings=Count('appointments'),
            total_revenue=Sum('appointments__payments__amount', default=0)
        ).all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Service ID', 'Name', 'Description', 'Price', 
                'Duration (min)', 'Total Bookings', 'Est. Revenue', 'Is Active'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for service in queryset:
                # Note: 'total_revenue' from annotation might include failed payments depending on query,
                # but for a simple report this is a good approximation. 
                # For stricter revenue, we'd filter appointments/payments first.
                writer.writerow({
                    'Service ID': service.id,
                    'Name': service.name,
                    'Description': service.description,
                    'Price': service.price,
                    'Duration (min)': service.duration_minutes,
                    'Total Bookings': service.total_bookings,
                    'Est. Revenue': service.total_revenue or 0,
                    'Is Active': service.is_active
                })
                
        self.stdout.write(f"  - Generated services.csv ({queryset.count()} records)")

    def generate_customers_report(self, output_dir):
        filepath = os.path.join(output_dir, 'customers.csv')
        # Filter for customers only and annotate
        queryset = User.objects.filter(role=User.Roles.CUSTOMER).annotate(
            total_bookings=Count('appointments'),
            last_booking=Max('appointments__start_at')
        )
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'User ID', 'Email', 'First Name', 'Last Name', 
                'Date Joined', 'Total Bookings', 'Last Booking Date', 'Is Active'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for user in queryset:
                writer.writerow({
                    'User ID': user.id,
                    'Email': user.email,
                    'First Name': user.first_name,
                    'Last Name': user.last_name,
                    'Date Joined': user.date_joined.isoformat(),
                    'Total Bookings': user.total_bookings,
                    'Last Booking Date': user.last_booking.isoformat() if user.last_booking else '',
                    'Is Active': user.is_active
                })
                
        self.stdout.write(f"  - Generated customers.csv ({queryset.count()} records)")
