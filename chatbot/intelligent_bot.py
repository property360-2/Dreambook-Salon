"""
Intelligent Chatbot with Database Queries and Role-Based Responses
"""
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from services.models import Service
from appointments.models import Appointment
from inventory.models import Item
from payments.models import Payment
import re


class IntelligentChatbot:
    """
    Smart chatbot that queries database for real-time information.
    Provides role-based responses for customers vs staff/admin.
    """

    def __init__(self, user=None):
        self.user = user
        self.is_staff = user and user.is_authenticated and user.role in ['ADMIN', 'STAFF']

    def process_message(self, message):
        """
        Process user message and return intelligent response.
        Detects intent and queries database accordingly.
        """
        message_lower = message.lower().strip()

        # Define intent patterns
        intents = [
            # Customer intents
            (r'\b(service|services|what do you (have|offer)|treatment)\b', self.get_services),
            (r'\b(price|cost|how much|pricing)\b', self.get_pricing),
            (r'\b(popular|best|top|most booked|trending)\b', self.get_popular_services),
            (r'\b(available|availability|book|appointment|schedule)\b', self.get_booking_info),
            (r'\b(hours|open|opening|when|time)\b', self.get_hours),
            (r'\b(location|address|where)\b', self.get_location),
            (r'\b(contact|phone|email|reach)\b', self.get_contact),

            # Staff/Admin intents (analytics)
            (r'\b(revenue|sales|income|earnings)\b', self.get_revenue_analytics),
            (r'\b(appointment stats|appointment count|bookings|total appointments)\b', self.get_appointment_stats),
            (r'\b(inventory|stock|low stock|out of stock)\b', self.get_inventory_status),
            (r'\b(top service|best performing|highest revenue)\b', self.get_top_services_analytics),
            (r'\b(payment|payment stats|transaction)\b', self.get_payment_analytics),
            (r'\b(today|daily)\b', self.get_today_summary),
            (r'\b(week|weekly)\b', self.get_week_summary),
            (r'\b(month|monthly)\b', self.get_month_summary),
            (r'\b(pending|confirmed|completed)\b', self.get_appointment_status_breakdown),
        ]

        # Try to match intent
        for pattern, handler in intents:
            if re.search(pattern, message_lower):
                # Check role permission for analytics queries
                if handler in [self.get_revenue_analytics, self.get_appointment_stats,
                              self.get_inventory_status, self.get_top_services_analytics,
                              self.get_payment_analytics, self.get_today_summary,
                              self.get_week_summary, self.get_month_summary,
                              self.get_appointment_status_breakdown]:
                    if not self.is_staff:
                        return "I'm sorry, but analytics information is only available to staff members. You can ask me about our services, pricing, or booking information!"

                return handler(message_lower)

        # Default response
        if self.is_staff:
            return ("I can help you with:\n"
                   "📊 Revenue analytics\n"
                   "📅 Appointment statistics\n"
                   "📦 Inventory status\n"
                   "📈 Top services analysis\n"
                   "💳 Payment reports\n"
                   "📱 Or ask about services and booking!")
        else:
            return ("I can help you with:\n"
                   "💇 Our services and treatments\n"
                   "💰 Pricing information\n"
                   "⭐ Popular services\n"
                   "📅 Booking and availability\n"
                   "📍 Location and contact info\n"
                   "What would you like to know?")

    # ===== CUSTOMER QUERIES =====

    def get_services(self, message):
        """Return list of available services."""
        services = Service.objects.filter(is_active=True)

        if not services.exists():
            return "We currently don't have any services listed. Please check back later!"

        response = "Here are our available services:\n\n"
        for service in services:
            response += f"💇 **{service.name}**\n"
            response += f"   Duration: {service.duration_minutes} minutes\n"
            response += f"   Price: ₱{service.price}\n"
            if service.description:
                response += f"   {service.description[:100]}...\n"
            response += "\n"

        response += "Would you like to book an appointment? Just let me know!"
        return response

    def get_pricing(self, message):
        """Return pricing information."""
        services = Service.objects.filter(is_active=True).order_by('price')

        if not services.exists():
            return "Please contact us for pricing information!"

        min_price = services.first().price
        max_price = services.last().price

        response = f"Our services range from ₱{min_price} to ₱{max_price}.\n\n"
        response += "Specific prices:\n"
        for service in services:
            response += f"• {service.name}: ₱{service.price}\n"

        return response

    def get_popular_services(self, message):
        """Return most popular/booked services."""
        top_services = Service.objects.filter(
            is_active=True
        ).annotate(
            booking_count=Count('appointment', filter=Q(appointment__status='COMPLETED'))
        ).order_by('-booking_count')[:5]

        if not top_services:
            return "All our services are great! Check out our full service list to find what suits you best."

        response = "Our most popular services are:\n\n"
        for i, service in enumerate(top_services, 1):
            response += f"{i}. **{service.name}** - ₱{service.price}\n"
            response += f"   {service.booking_count} customers have chosen this!\n\n"

        response += "These are customer favorites! Would you like to book one?"
        return response

    def get_booking_info(self, message):
        """Return booking information."""
        return ("📅 **How to Book an Appointment:**\n\n"
               "1. Browse our services to choose your treatment\n"
               "2. Click 'Book Now' or 'Plan an appointment'\n"
               "3. Select your preferred date and time\n"
               "4. Confirm your booking\n\n"
               "We accept online bookings up to 30 days in advance!\n"
               "You can also view and manage your appointments in 'My Appointments'.")

    def get_hours(self, message):
        """Return business hours."""
        return ("⏰ **Opening Hours:**\n\n"
               "Monday - Friday: 9:00 AM - 7:00 PM\n"
               "Saturday: 9:00 AM - 8:00 PM\n"
               "Sunday: 10:00 AM - 6:00 PM\n\n"
               "We're here to make you look and feel amazing!")

    def get_location(self, message):
        """Return location information."""
        return ("📍 **Location:**\n\n"
               "Dreambook Salon\n"
               "Manila, Philippines\n\n"
               "We're located in the heart of Manila, easily accessible by public transport.\n"
               "Looking forward to seeing you!")

    def get_contact(self, message):
        """Return contact information."""
        return ("📞 **Contact Us:**\n\n"
               "Email: info@dreambooksalon.com\n"
               "Phone: +63 XXX XXX XXXX\n\n"
               "You can also book directly through our website or send us a message here!")

    # ===== STAFF/ADMIN ANALYTICS QUERIES =====

    def get_revenue_analytics(self, message):
        """Return revenue analytics (staff/admin only)."""
        today = timezone.now().date()

        # Total revenue
        total_revenue = Payment.objects.filter(
            status='PAID'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # This month
        month_revenue = Payment.objects.filter(
            status='PAID',
            created_at__year=today.year,
            created_at__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Today
        today_revenue = Payment.objects.filter(
            status='PAID',
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0

        response = "💰 **Revenue Analytics:**\n\n"
        response += f"Total All-Time: ₱{total_revenue:,.2f}\n"
        response += f"This Month: ₱{month_revenue:,.2f}\n"
        response += f"Today: ₱{today_revenue:,.2f}\n"

        return response

    def get_appointment_stats(self, message):
        """Return appointment statistics (staff/admin only)."""
        total = Appointment.objects.count()
        pending = Appointment.objects.filter(status='PENDING').count()
        confirmed = Appointment.objects.filter(status='CONFIRMED').count()
        completed = Appointment.objects.filter(status='COMPLETED').count()
        cancelled = Appointment.objects.filter(status='CANCELLED').count()

        response = "📅 **Appointment Statistics:**\n\n"
        response += f"Total Appointments: {total}\n"
        response += f"Pending: {pending}\n"
        response += f"Confirmed: {confirmed}\n"
        response += f"Completed: {completed}\n"
        response += f"Cancelled: {cancelled}\n"

        if total > 0:
            completion_rate = (completed / total) * 100
            response += f"\n✅ Completion Rate: {completion_rate:.1f}%"

        return response

    def get_inventory_status(self, message):
        """Return inventory status (staff/admin only)."""
        total_items = Item.objects.filter(is_active=True).count()
        low_stock = Item.objects.filter(is_active=True, is_low_stock=True).count()
        out_of_stock = Item.objects.filter(is_active=True, stock__lte=0).count()

        response = "📦 **Inventory Status:**\n\n"
        response += f"Total Items: {total_items}\n"
        response += f"⚠️ Low Stock: {low_stock}\n"
        response += f"🚨 Out of Stock: {out_of_stock}\n"

        if out_of_stock > 0:
            out_items = Item.objects.filter(is_active=True, stock__lte=0)[:3]
            response += "\nCritical Items:\n"
            for item in out_items:
                response += f"• {item.name}\n"

        return response

    def get_top_services_analytics(self, message):
        """Return top performing services (staff/admin only)."""
        top_services = Service.objects.annotate(
            booking_count=Count('appointment', filter=Q(appointment__status='COMPLETED')),
            total_revenue=Sum('appointment__payment__amount',
                            filter=Q(appointment__payment__status='PAID'))
        ).order_by('-booking_count')[:5]

        response = "📈 **Top Performing Services:**\n\n"
        for i, service in enumerate(top_services, 1):
            response += f"{i}. {service.name}\n"
            response += f"   Bookings: {service.booking_count or 0}\n"
            response += f"   Revenue: ₱{service.total_revenue or 0:,.2f}\n\n"

        return response

    def get_payment_analytics(self, message):
        """Return payment analytics (staff/admin only)."""
        total_payments = Payment.objects.count()
        paid = Payment.objects.filter(status='PAID').count()
        pending = Payment.objects.filter(status='PENDING').count()
        failed = Payment.objects.filter(status='FAILED').count()

        # Payment methods breakdown
        gcash = Payment.objects.filter(method='GCASH', status='PAID').count()
        paymaya = Payment.objects.filter(method='PAYMAYA', status='PAID').count()
        onsite = Payment.objects.filter(method='ONSITE', status='PAID').count()

        response = "💳 **Payment Analytics:**\n\n"
        response += f"Total Payments: {total_payments}\n"
        response += f"✅ Paid: {paid}\n"
        response += f"⏳ Pending: {pending}\n"
        response += f"❌ Failed: {failed}\n\n"
        response += "Payment Methods:\n"
        response += f"GCash: {gcash}\n"
        response += f"PayMaya: {paymaya}\n"
        response += f"Onsite/Cash: {onsite}\n"

        return response

    def get_today_summary(self, message):
        """Return today's summary (staff/admin only)."""
        today = timezone.now().date()

        appointments_today = Appointment.objects.filter(
            start_at__date=today
        ).count()

        revenue_today = Payment.objects.filter(
            status='PAID',
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0

        response = "📊 **Today's Summary:**\n\n"
        response += f"Date: {today.strftime('%B %d, %Y')}\n"
        response += f"Appointments: {appointments_today}\n"
        response += f"Revenue: ₱{revenue_today:,.2f}\n"

        return response

    def get_week_summary(self, message):
        """Return this week's summary (staff/admin only)."""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        appointments_week = Appointment.objects.filter(
            start_at__date__gte=week_start
        ).count()

        revenue_week = Payment.objects.filter(
            status='PAID',
            created_at__date__gte=week_start
        ).aggregate(total=Sum('amount'))['total'] or 0

        response = "📊 **This Week's Summary:**\n\n"
        response += f"Appointments: {appointments_week}\n"
        response += f"Revenue: ₱{revenue_week:,.2f}\n"

        return response

    def get_month_summary(self, message):
        """Return this month's summary (staff/admin only)."""
        today = timezone.now()

        appointments_month = Appointment.objects.filter(
            start_at__year=today.year,
            start_at__month=today.month
        ).count()

        revenue_month = Payment.objects.filter(
            status='PAID',
            created_at__year=today.year,
            created_at__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        response = "📊 **This Month's Summary:**\n\n"
        response += f"Month: {today.strftime('%B %Y')}\n"
        response += f"Appointments: {appointments_month}\n"
        response += f"Revenue: ₱{revenue_month:,.2f}\n"

        return response

    def get_appointment_status_breakdown(self, message):
        """Return appointment status breakdown (staff/admin only)."""
        statuses = Appointment.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        response = "📋 **Appointment Status Breakdown:**\n\n"
        for status_data in statuses:
            status = status_data['status']
            count = status_data['count']
            emoji = {
                'PENDING': '⏳',
                'CONFIRMED': '✅',
                'IN_PROGRESS': '🔄',
                'COMPLETED': '✔️',
                'NO_SHOW': '❌',
                'CANCELLED': '🚫'
            }.get(status, '•')

            response += f"{emoji} {status.replace('_', ' ').title()}: {count}\n"

        return response
