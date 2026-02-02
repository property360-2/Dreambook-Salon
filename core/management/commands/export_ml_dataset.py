import csv
import sys
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum

# Import your models here
# We use string imports or direct imports inside the method if avoiding circular deps,
# but for a management command, top-level imports are fine if apps are loaded.
from appointments.models import Appointment
from payments.models import Payment

class Command(BaseCommand):
    help = 'Exports a machine-learning ready dataset from the database to CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='ml_dataset.csv',
            help='Output CSV file path'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        self.stdout.write(f"Generating dataset to {output_file}...")

        try:
            # defined extraction logic
            data_rows = self.extract_data()
            
            if not data_rows:
                self.stdout.write(self.style.WARNING("No data found to export."))
                return

            # Write to CSV
            fieldnames = data_rows[0].keys()
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data_rows:
                    writer.writerow(row)

            self.stdout.write(self.style.SUCCESS(f"Successfully exported {len(data_rows)} rows to {output_file}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating dataset: {str(e)}"))

    def extract_data(self):
        """
        Main logic to fetch and flatten data.
        Returns a list of dictionaries, where each dict is a row.
        """
        dataset = []
        
        # Optimize query with select_related for FKs
        # fetching all appointments as our "logical record"
        appointments = Appointment.objects.all().select_related(
            'service', 
            'customer'
        ).prefetch_related('payments')

        for appt in appointments:
            # ---------------------------------------------------------
            # FEATURE ENGINEERING
            # ---------------------------------------------------------
            
            # 1. Booking Lead Time (in hours)
            # Handle potential missing created_at if legacy data (though auto_now_add usually ensures it)
            if appt.created_at and appt.start_at:
                lead_time = (appt.start_at - appt.created_at).total_seconds() / 3600.0
                lead_time = max(0.0, lead_time) # Ensure no negative time
            else:
                lead_time = 0.0

            # 2. Time Features
            # Extract numerical components from datetime
            start_hour = appt.start_at.hour
            day_of_week = appt.start_at.weekday() # 0=Monday, 6=Sunday
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # 3. Service Features
            # Service duration and price are good predictors
            service_duration = appt.service.duration_minutes
            service_base_price = float(appt.service.price)

            # ---------------------------------------------------------
            # TARGET VARIABLE
            # ---------------------------------------------------------
            # We want to predict the "Total Amount Paid" (Revenue)
            # This handles cases where refunds occurred or partial payments if supported
            # For this system, we sum up successful payments associated with the appointment.
            
            # Note: We use the reverse relation 'payment_set' or similar. 
            # Based on model inspection, Payment has FK to appointment.
            
            total_paid = 0.0
            payments = appt.payments.all()
            for p in payments:
                if p.status == 'paid': # Only count successful payments
                    total_paid += float(p.amount)
            
            # ---------------------------------------------------------
            # ROW CONSTRUCTION
            # ---------------------------------------------------------
            row = {
                # --- Features ---
                'lead_time_hours': round(lead_time, 2),
                'start_hour': start_hour,
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'service_duration_mins': service_duration,
                'service_base_price': service_base_price,
                
                # --- Target ---
                'target_total_paid': total_paid
            }
            
            dataset.append(row)

        return dataset
