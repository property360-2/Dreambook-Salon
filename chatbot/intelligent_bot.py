"""
Intelligent Chatbot with Database Queries and Role-Based Responses
Enhanced with Filipino/Taglish support and advanced queries
"""
from django.db.models import Count, Sum, Avg, Q, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from services.models import Service
from appointments.models import Appointment
from inventory.models import Item
from payments.models import Payment
import re


class IntelligentChatbot:
    """
    Smart chatbot that queries database for real-time information.
    Provides role-based responses for customers vs staff/admin.
    Supports English and Filipino/Taglish queries.
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

        # Try specific queries first (more specific patterns)

        # Specific service/product price query
        specific_price = self.check_specific_price(message_lower)
        if specific_price:
            return specific_price

        # Service duration query
        specific_duration = self.check_service_duration(message_lower)
        if specific_duration:
            return specific_duration

        # Appointment availability on specific date
        date_availability = self.check_date_availability(message_lower)
        if date_availability:
            return date_availability

        # Historical analytics queries (staff only)
        if self.is_staff:
            historical_data = self.check_historical_query(message_lower)
            if historical_data:
                return historical_data

        # Define general intent patterns
        intents = [
            # Customer intents (English + Filipino)
            (r'\b(service|services|what do you (have|offer)|treatment|serbisyo|ano (ang|meron))\b', self.get_services),
            (r'\b(price|cost|how much|pricing|magkano|presyo)\b', self.get_pricing),
            (r'\b(popular|best|top|most booked|trending|sikat|pinaka|best selling|best\s?seller|bestseller|pinakasikat)\b', self.get_popular_services),
            (r'\b(available|availability|book|appointment|schedule|may slot|meron bang|pwede (ba|bang)|libre)\b', self.get_booking_info),
            (r'\b(hours|open|opening|when|time|bukas|oras|anong oras)\b', self.get_hours),
            (r'\b(location|address|where|saan|nasaan)\b', self.get_location),
            (r'\b(contact|phone|email|reach|number|tawag)\b', self.get_contact),
            (r'\b(inventory|item|items|product|gamit)\b', self.get_inventory_info),

            # Staff/Admin intents (analytics) - English + Filipino
            (r'\b(revenue|sales|income|earnings|kita|benta|profit|kikita)\b', self.get_revenue_analytics),
            (r'\b(appointment stats|appointment count|bookings|total appointments|bilang|dami)\b', self.get_appointment_stats),
            (r'\b(inventory status|stock|low stock|out of stock|kulang|ubos)\b', self.get_inventory_status),
            (r'\b(top service|best performing|highest revenue|pinaka mataas|best selling|pinakasikat|numero uno|number one)\b', self.get_top_services_analytics),
            (r'\b(payment|payment stats|transaction|bayad|pera)\b', self.get_payment_analytics),
            (r'\b(today|daily|ngayon|ngayong araw)\b', self.get_today_summary),
            (r'\b(week|weekly|linggo|this week)\b', self.get_week_summary),
            (r'\b(month|monthly|buwan|this month)\b', self.get_month_summary),
            (r'\b(pending|confirmed|completed|status)\b', self.get_appointment_status_breakdown),

            # Advanced Intelligence Queries (Staff/Admin Only)
            (r'\b(most (booked|popular|best selling)|bestselling|pinakasikat|best seller|numero uno|top 1|top services|profitable|highest earning)\b', self.get_best_selling_service_detailed),
            (r'\b(customer (analysis|analytics|insights|trends)|client|satisfaction|retention|repeat|loyalty|engagement)\b', self.get_customer_analytics),
            (r'\b(staff|employee|therapist|performance|productivity|top performer|best staff)\b', self.get_staff_analytics),
            (r'\b(peak (hours|times|periods)|busy|busiest|rush hour|peak demand)\b', self.get_peak_hours_analysis),
            (r'\b(average|avg|spending|spend|price range|revenue per|income per|earning per)\b', self.get_spending_analytics),
            (r'\b(no[\\-]?show|cancelation|cancel rate|noshow rate|absence|failed|missed)\b', self.get_noshow_analytics),
            (r'\b(growth|trend|increase|decrease|comparison|vs|previous|period)\b', self.get_growth_analytics),
            (r'\b(profitability|profitable|profit margin|margin|cost|efficiency)\b', self.get_profitability_analysis),
            (r'\b(recommendation|suggest|which (service|treatment)|what should|ano (ang best|dapat))\b', self.get_service_recommendations),
            (r'\b(forecast|predict|projection|estimate|expected|upcoming)\b', self.get_forecast_analysis),
        ]

        # Try to match intent
        for pattern, handler in intents:
            if re.search(pattern, message_lower):
                # Check role permission for analytics queries
                analytics_handlers = [
                    self.get_revenue_analytics, self.get_appointment_stats,
                    self.get_inventory_status, self.get_top_services_analytics,
                    self.get_payment_analytics, self.get_today_summary,
                    self.get_week_summary, self.get_month_summary,
                    self.get_appointment_status_breakdown,
                    self.get_best_selling_service_detailed, self.get_customer_analytics,
                    self.get_staff_analytics, self.get_peak_hours_analysis,
                    self.get_spending_analytics, self.get_noshow_analytics,
                    self.get_growth_analytics, self.get_profitability_analysis,
                    self.get_service_recommendations, self.get_forecast_analysis
                ]

                if handler in analytics_handlers:
                    if not self.is_staff:
                        return "I'm sorry, but analytics information is only available to staff members. You can ask me about our services, pricing, or booking information!\n\n(Pasensya na, pero ang analytics ay para lang sa staff. Magtanong ka tungkol sa aming services, presyo, o booking!)"

                return handler(message_lower)

        # Default response
        if self.is_staff:
            return ("I can help you with ADVANCED ANALYTICS:\n"
                   "🏆 **Best selling service** (most booked, bestseller, pinakasikat)\n"
                   "👥 **Customer insights** (retention, loyalty, satisfaction)\n"
                   "💼 **Staff performance** (productivity, top performer)\n"
                   "⏰ **Peak hours** (busy times, rush hours)\n"
                   "💰 **Spending analysis** (average, revenue per customer)\n"
                   "📊 **No-show analytics** (cancelation, absence rates)\n"
                   "📈 **Growth trends** (comparison, growth, decline)\n"
                   "💵 **Profitability** (profit margin, most profitable)\n"
                   "🔮 **Forecast** (predictions, projections, expected)\n\n"
                   "BASIC ANALYTICS:\n"
                   "💰 Revenue, 📅 Appointments, 📦 Inventory, 💳 Payments, 🔍 Status\n\n"
                   "SPECIFIC QUERIES:\n"
                   "📱 'best selling service?', 'customer retention?', 'peak hours?', 'what will revenue be next month?'\n\n"
                   "Or ask about services and booking!")
        else:
            return ("I can help you with:\n"
                   "💇 Our services and treatments (services, serbisyo)\n"
                   "💰 Pricing information (magkano, price)\n"
                   "⭐ Popular services (popular, sikat)\n"
                   "📅 Booking and availability (available, meron bang)\n"
                   "⏱️ Service duration (how long, gaano katagal)\n"
                   "📍 Location and contact (location, saan)\n\n"
                   "Examples:\n"
                   "• 'How much is the haircut?'\n"
                   "• 'Magkano ang hair spa?'\n"
                   "• 'How long is the massage?'\n"
                   "• 'Meron bang appointment sa 12/26/2025?'")

    # ===== SPECIFIC QUERY HANDLERS =====

    def check_specific_price(self, message):
        """Check if asking about specific service/product price."""
        # Patterns: "how much is X", "magkano ang X", "price of X", "X price"
        patterns = [
            r'(?:how much|magkano)(?: is| ang| yung| si)? (?:the |ang )?(.*?)(?:\?|$)',
            r'(?:price|presyo)(?: of| ng)? (?:the |ang )?(.*?)(?:\?|$)',
            r'(.*?)(?: price| presyo| magkano)(?:\?|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                search_term = match.group(1).strip()
                if search_term and len(search_term) > 2:
                    # Clean up common words
                    search_term = re.sub(r'\b(yung|ang|the|this|that|is|ay)\b', '', search_term).strip()

                    # Search in services
                    service = Service.objects.filter(
                        Q(name__icontains=search_term) | Q(description__icontains=search_term),
                        is_active=True
                    ).first()

                    if service:
                        response = f"💇 **{service.name}**\n\n"
                        response += f"Price: **₱{service.price}**\n"
                        response += f"Duration: {service.duration_minutes} minutes\n\n"
                        if service.description:
                            response += f"{service.description}\n\n"
                        response += "Would you like to book this service?"
                        return response

                    # Search in inventory (staff only)
                    if self.is_staff:
                        item = Item.objects.filter(
                            Q(name__icontains=search_term),
                            is_active=True
                        ).first()

                        if item:
                            response = f"📦 **{item.name}**\n\n"
                            response += f"Stock: {item.stock} {item.unit}\n"
                            response += f"Threshold: {item.threshold} {item.unit}\n"
                            if item.is_low_stock:
                                response += "⚠️ **Low Stock Alert**"
                            return response

                    # If no match found
                    return f"I couldn't find information about '{search_term}'. Try asking about our available services or check the services page!"

        return None

    def check_service_duration(self, message):
        """Check if asking about specific service duration."""
        # Patterns: "how long is X", "gaano katagal ang X", "duration of X"
        patterns = [
            r'(?:how long|gaano katagal)(?: is| ang| yung)? (?:the |ang )?(.*?)(?:\?|$)',
            r'(?:duration|tagal)(?: of| ng)? (?:the |ang )?(.*?)(?:\?|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                search_term = match.group(1).strip()
                if search_term and len(search_term) > 2:
                    # Clean up common words
                    search_term = re.sub(r'\b(yung|ang|the|this|that|is|ay)\b', '', search_term).strip()

                    service = Service.objects.filter(
                        Q(name__icontains=search_term) | Q(description__icontains=search_term),
                        is_active=True
                    ).first()

                    if service:
                        response = f"⏱️ **{service.name}**\n\n"
                        response += f"Duration: **{service.duration_minutes} minutes**\n"
                        response += f"Price: ₱{service.price}\n\n"
                        response += "Perfect timing for a premium pampering session! Would you like to book?"
                        return response

                    return f"I couldn't find information about '{search_term}'. Check our services page for all available treatments!"

        return None

    def check_date_availability(self, message):
        """Check appointment availability on specific date."""
        # Patterns: "meron bang appointment sa X", "available on X", "may slot ba sa X"
        patterns = [
            r'(?:meron bang|may|available|libre|pwede)(?: appointment| slot| ba)?(?: sa| on| sa araw ng)? (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})(?: available| may slot| meron)',
            r'(?:book|appointment|schedule)(?: on| sa)? (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                date_str = match.group(1)

                # Parse date (support multiple formats)
                parsed_date = None
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%y', '%m-%d-%y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue

                if not parsed_date:
                    return f"I couldn't understand the date format '{date_str}'. Please use MM/DD/YYYY (e.g., 12/26/2025)"

                # Check if date is in the past
                today = timezone.now().date()
                if parsed_date < today:
                    return f"That date ({parsed_date.strftime('%B %d, %Y')}) is in the past! Please choose a future date."

                # Check appointments on that date
                appointments_on_date = Appointment.objects.filter(
                    start_at__date=parsed_date
                ).count()

                # Assume max 10 appointments per day (you can adjust)
                max_daily_appointments = 10
                available_slots = max_daily_appointments - appointments_on_date

                response = f"📅 **Availability for {parsed_date.strftime('%B %d, %Y')}**\n\n"

                if available_slots > 0:
                    response += f"✅ **{available_slots} slots available!**\n\n"
                    response += "We have openings on this date. You can book an appointment:\n"
                    response += "1. Click 'Book Now' or 'Plan an appointment'\n"
                    response += f"2. Select {parsed_date.strftime('%B %d, %Y')}\n"
                    response += "3. Choose your preferred time slot\n\n"
                    response += "Looking forward to pampering you! 💇✨"
                else:
                    response += f"⚠️ **Fully booked**\n\n"
                    response += "This date is currently full. Would you like to:\n"
                    response += "• Choose a different date?\n"
                    response += "• Check our other available dates?\n"
                    response += "• Contact us for more options?"

                return response

        return None

    def check_historical_query(self, message):
        """Check for historical date queries (staff only)."""
        if not self.is_staff:
            return None

        today = timezone.now().date()
        target_date = None
        period_name = ""

        # Pattern: "last friday", "last monday", etc.
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6,
            'lunes': 0, 'martes': 1, 'miyerkules': 2, 'huwebes': 3,
            'biyernes': 4, 'sabado': 5, 'linggo': 6
        }

        for day_name, day_num in weekdays.items():
            if f'last {day_name}' in message or f'nakaraang {day_name}' in message:
                days_ago = (today.weekday() - day_num) % 7
                if days_ago == 0:
                    days_ago = 7
                target_date = today - timedelta(days=days_ago)
                period_name = f"Last {day_name.title()}"
                break

        # Pattern: "yesterday", "kahapon"
        if 'yesterday' in message or 'kahapon' in message:
            target_date = today - timedelta(days=1)
            period_name = "Yesterday"

        # Pattern: "last week", "nakaraang linggo"
        if 'last week' in message or 'nakaraang linggo' in message:
            week_ago = today - timedelta(days=7)
            target_date = week_ago
            period_name = "Last Week"
            # For week, get range
            week_start = week_ago - timedelta(days=week_ago.weekday())
            week_end = week_start + timedelta(days=6)

            return self._get_period_analytics(week_start, week_end, period_name)

        # Pattern: "last month", "nakaraang buwan"
        if 'last month' in message or 'nakaraang buwan' in message:
            if today.month == 1:
                last_month = today.replace(year=today.year-1, month=12, day=1)
            else:
                last_month = today.replace(month=today.month-1, day=1)

            # Get last day of last month
            if last_month.month == 12:
                month_end = last_month.replace(year=last_month.year+1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = last_month.replace(month=last_month.month+1, day=1) - timedelta(days=1)

            period_name = last_month.strftime("Last Month (%B %Y)")
            return self._get_period_analytics(last_month, month_end, period_name)

        # If we have a specific date
        if target_date:
            return self._get_daily_analytics(target_date, period_name)

        return None

    def _get_daily_analytics(self, date, period_name):
        """Get analytics for a specific day (staff only)."""
        appointments = Appointment.objects.filter(start_at__date=date).count()
        revenue = Payment.objects.filter(
            status='PAID',
            created_at__date=date
        ).aggregate(total=Sum('amount'))['total'] or 0

        completed = Appointment.objects.filter(
            start_at__date=date,
            status='COMPLETED'
        ).count()

        response = f"📊 **{period_name} Analytics**\n\n"
        response += f"Date: {date.strftime('%B %d, %Y')}\n"
        response += f"Total Appointments: {appointments}\n"
        response += f"Completed: {completed}\n"
        response += f"Revenue: ₱{revenue:,.2f}\n"

        return response

    def _get_period_analytics(self, start_date, end_date, period_name):
        """Get analytics for a date range (staff only)."""
        appointments = Appointment.objects.filter(
            start_at__date__gte=start_date,
            start_at__date__lte=end_date
        ).count()

        revenue = Payment.objects.filter(
            status='PAID',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0

        completed = Appointment.objects.filter(
            start_at__date__gte=start_date,
            start_at__date__lte=end_date,
            status='COMPLETED'
        ).count()

        response = f"📊 **{period_name} Analytics**\n\n"
        response += f"Period: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}\n"
        response += f"Total Appointments: {appointments}\n"
        response += f"Completed: {completed}\n"
        response += f"Revenue: ₱{revenue:,.2f}\n"

        return response

    # ===== CUSTOMER QUERIES =====

    def get_services(self, message):
        """Return list of available services."""
        services = Service.objects.filter(is_active=True)

        if not services.exists():
            return "We currently don't have any services listed. Please check back later!\n\n(Wala pang available na services ngayon. Balik kayo soon!)"

        response = "Here are our available services:\n\n"
        for service in services:
            response += f"💇 **{service.name}**\n"
            response += f"   Duration: {service.duration_minutes} minutes\n"
            response += f"   Price: ₱{service.price}\n"
            if service.description:
                response += f"   {service.description[:100]}...\n"
            response += "\n"

        response += "Would you like to book an appointment? Just let me know!\n(Gusto mo bang mag-book? Sabihin mo lang!)"
        return response

    def get_pricing(self, message):
        """Return pricing information."""
        services = Service.objects.filter(is_active=True).order_by('price')

        if not services.exists():
            return "Please contact us for pricing information!"

        min_price = services.first().price
        max_price = services.last().price

        response = f"Our services range from ₱{min_price} to ₱{max_price}.\n\n"
        response += "Specific prices (Mga presyo):\n"
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
            return "All our services are great! Check out our full service list to find what suits you best.\n\n(Lahat ng services namin ay magaganda! Tingnan ang buong listahan!)"

        response = "Our most popular services (Mga sikat na services):\n\n"
        for i, service in enumerate(top_services, 1):
            response += f"{i}. **{service.name}** - ₱{service.price}\n"
            response += f"   {service.booking_count} customers have chosen this!\n\n"

        response += "These are customer favorites! Would you like to book one?\n(Ito ang mga paborito ng customers! Book na?)"
        return response

    def get_booking_info(self, message):
        """Return booking information."""
        return ("📅 **How to Book an Appointment:**\n\n"
               "1. Browse our services to choose your treatment\n"
               "2. Click 'Book Now' or 'Plan an appointment'\n"
               "3. Select your preferred date and time\n"
               "4. Confirm your booking\n\n"
               "**Paano Mag-book:**\n"
               "1. Piliin ang gusto mong treatment\n"
               "2. Click 'Book Now'\n"
               "3. Pumili ng date at time\n"
               "4. I-confirm ang booking\n\n"
               "We accept online bookings up to 30 days in advance!\n"
               "You can also view and manage your appointments in 'My Appointments'.")

    def get_hours(self, message):
        """Return business hours."""
        return ("⏰ **Opening Hours (Oras ng Pagbubukas):**\n\n"
               "Monday - Friday: 9:00 AM - 7:00 PM\n"
               "Saturday: 9:00 AM - 8:00 PM\n"
               "Sunday: 10:00 AM - 6:00 PM\n\n"
               "We're here to make you look and feel amazing!\n"
               "Nandito kami para pagandahin ka! 💇✨")

    def get_location(self, message):
        """Return location information."""
        return ("📍 **Location:**\n\n"
               "Dreambook Salon\n"
               "Manila, Philippines\n\n"
               "We're located in the heart of Manila, easily accessible by public transport.\n"
               "Nasa gitna ng Manila kami, madaling puntahan!\n\n"
               "Looking forward to seeing you! (Abangan ka namin!)")

    def get_contact(self, message):
        """Return contact information."""
        return ("📞 **Contact Us:**\n\n"
               "Email: info@dreambooksalon.com\n"
               "Phone: +63 XXX XXX XXXX\n\n"
               "You can also book directly through our website or send us a message here!\n"
               "Pwede rin mag-book dito sa website o mag-message lang!")

    def get_inventory_info(self, message):
        """Return available inventory items (customer version)."""
        if self.is_staff:
            return self.get_inventory_status(message)

        # For customers, show general product info
        return ("We use only premium, high-quality products for all our treatments:\n\n"
               "• Professional hair care products\n"
               "• Premium styling tools\n"
               "• Top-grade salon equipment\n\n"
               "Your satisfaction and safety are our priorities!\n"
               "Gumagamit kami ng premium products para sa lahat!")

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

    # ===== ADVANCED INTELLIGENCE ANALYTICS =====

    def get_best_selling_service_detailed(self, message):
        """Return detailed best selling/most booked service analysis (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        # Get best selling service by bookings
        best_service = Service.objects.annotate(
            booking_count=Count('appointment', filter=Q(appointment__status='COMPLETED')),
            total_revenue=Sum('appointment__payment__amount',
                            filter=Q(appointment__payment__status='PAID')),
            avg_rating=Avg('appointment__payment__amount',
                         filter=Q(appointment__payment__status='PAID'))
        ).order_by('-booking_count').first()

        if not best_service or best_service.booking_count == 0:
            return "No completed appointments yet. Start tracking bookings to see analytics!"

        # Calculate metrics
        all_completed = Appointment.objects.filter(status='COMPLETED').count()
        market_share = (best_service.booking_count / all_completed * 100) if all_completed > 0 else 0

        response = f"🏆 **Best Selling Service Analysis**\n\n"
        response += f"📌 Service: **{best_service.name}**\n"
        response += f"💇 Price: ₱{best_service.price}\n\n"

        response += f"**Performance Metrics:**\n"
        response += f"✅ Total Bookings: {best_service.booking_count}\n"
        response += f"📊 Market Share: {market_share:.1f}%\n"
        response += f"💰 Total Revenue: ₱{best_service.total_revenue or 0:,.2f}\n"
        response += f"💵 Avg Revenue per Booking: ₱{best_service.price:,.2f}\n"

        # Compare with others
        second_best = Service.objects.annotate(
            booking_count=Count('appointment', filter=Q(appointment__status='COMPLETED'))
        ).exclude(id=best_service.id).order_by('-booking_count').first()

        if second_best:
            lead = best_service.booking_count - second_best.booking_count
            response += f"\n📈 Leading {second_best.name} by {lead} bookings\n"

        response += f"\n✨ This is your star service! Focus on marketing and maintaining quality!"

        return response

    def get_customer_analytics(self, message):
        """Return customer insights and behavior analytics (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        from django.contrib.auth import get_user_model
        User = get_user_model()

        total_customers = User.objects.filter(role='CUSTOMER').count()
        repeat_customers = User.objects.filter(
            role='CUSTOMER',
            appointments__status='COMPLETED'
        ).distinct().annotate(
            appointment_count=Count('appointments')
        ).filter(appointment_count__gte=2).count()

        total_appointments = Appointment.objects.filter(status='COMPLETED').count()
        avg_customer_value = Payment.objects.filter(status='PAID').aggregate(
            total=Sum('amount')
        )['total'] or 0

        response = "👥 **Customer Analytics & Insights:**\n\n"
        response += f"Total Customers: {total_customers}\n"
        response += f"🔄 Repeat Customers: {repeat_customers}\n"

        if total_customers > 0:
            retention_rate = (repeat_customers / total_customers) * 100
            response += f"📈 Customer Retention Rate: {retention_rate:.1f}%\n"

        if total_customers > 0 and avg_customer_value > 0:
            avg_value = avg_customer_value / total_customers
            response += f"\n💰 **Customer Value:**\n"
            response += f"Total Revenue: ₱{avg_customer_value:,.2f}\n"
            response += f"Avg Value per Customer: ₱{avg_value:,.2f}\n"

        response += f"\nTotal Completed Appointments: {total_appointments}\n"

        if total_customers > 0:
            appointments_per_customer = total_appointments / total_customers
            response += f"Avg Appointments per Customer: {appointments_per_customer:.1f}\n"

        return response

    def get_staff_analytics(self, message):
        """Return staff performance analytics (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        from django.contrib.auth import get_user_model
        User = get_user_model()

        total_staff = User.objects.filter(role__in=['STAFF', 'ADMIN']).count()

        response = "👔 **Staff Performance Analytics:**\n\n"
        response += f"Total Staff Members: {total_staff}\n\n"

        # Get total workload
        completed_appointments = Appointment.objects.filter(status='COMPLETED').count()
        response += f"📊 Total Completed Services: {completed_appointments}\n"

        if total_staff > 0:
            avg_per_staff = completed_appointments / total_staff
            response += f"Avg per Staff Member: {avg_per_staff:.1f}\n\n"

        response += "💡 **Insights:**\n"
        response += "• Monitor individual staff productivity\n"
        response += "• Recognize top performers\n"
        response += "• Ensure balanced workload distribution\n"

        return response

    def get_peak_hours_analysis(self, message):
        """Analyze peak booking hours and times (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        # Get busiest hours
        from django.db.models.functions import Hour
        peak_hours = Appointment.objects.filter(
            status__in=['CONFIRMED', 'IN_PROGRESS', 'COMPLETED']
        ).annotate(hour=Hour('start_at')).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:3]

        response = "⏰ **Peak Hours Analysis:**\n\n"

        if peak_hours:
            response += "**Busiest Times:**\n"
            for i, hour_data in enumerate(peak_hours, 1):
                hour = hour_data['hour']
                count = hour_data['count']
                if hour is not None:
                    time_str = f"{hour:02d}:00 - {hour:02d}:59"
                    response += f"{i}. {time_str}: {count} appointments\n"
        else:
            response += "No appointment data available yet.\n"

        response += f"\n📈 **Recommendations:**\n"
        response += "• Schedule staff based on peak hours\n"
        response += "• Encourage off-peak bookings with special offers\n"
        response += "• Prepare inventory for high-demand periods\n"

        return response

    def get_spending_analytics(self, message):
        """Analyze customer spending patterns (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        all_payments = Payment.objects.filter(status='PAID').aggregate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount'),
            max=Max('amount'),
            min=Min('amount')
        )

        response = "💰 **Spending Analytics:**\n\n"
        response += f"**Total Revenue:** ₱{all_payments['total'] or 0:,.2f}\n"
        response += f"**Transaction Count:** {all_payments['count'] or 0}\n\n"

        if all_payments['count'] and all_payments['count'] > 0:
            response += f"**Spending Range:**\n"
            response += f"• Average: ₱{all_payments['avg'] or 0:,.2f}\n"
            response += f"• Highest: ₱{all_payments['max'] or 0:,.2f}\n"
            response += f"• Lowest: ₱{all_payments['min'] or 0:,.2f}\n\n"

        # Price distribution
        services = Service.objects.all().values('price').distinct().order_by('price')
        if services:
            prices = [s['price'] for s in services]
            response += f"**Service Price Range:** ₱{min(prices)} - ₱{max(prices)}\n"

        return response

    def get_noshow_analytics(self, message):
        """Analyze no-show and cancellation rates (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        total = Appointment.objects.count()
        no_shows = Appointment.objects.filter(status='NO_SHOW').count()
        cancelled = Appointment.objects.filter(status='CANCELLED').count()
        completed = Appointment.objects.filter(status='COMPLETED').count()

        response = "📊 **No-Show & Cancellation Analysis:**\n\n"
        response += f"Total Appointments: {total}\n"
        response += f"🚫 No-Shows: {no_shows}\n"
        response += f"❌ Cancellations: {cancelled}\n"
        response += f"✅ Completed: {completed}\n\n"

        if total > 0:
            no_show_rate = (no_shows / total) * 100
            cancel_rate = (cancelled / total) * 100
            completion_rate = (completed / total) * 100

            response += f"**Rates:**\n"
            response += f"No-Show Rate: {no_show_rate:.1f}%\n"
            response += f"Cancellation Rate: {cancel_rate:.1f}%\n"
            response += f"✅ Completion Rate: {completion_rate:.1f}%\n\n"

            response += "💡 **Action Items:**\n"
            if no_show_rate > 10:
                response += "⚠️ High no-show rate! Consider SMS reminders.\n"
            if cancel_rate > 15:
                response += "⚠️ High cancellation rate! Review policies.\n"

        return response

    def get_growth_analytics(self, message):
        """Analyze business growth trends (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        prev_month_end = current_month_start - timedelta(days=1)

        # Current month
        current_revenue = Payment.objects.filter(
            status='PAID',
            created_at__gte=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0

        current_appointments = Appointment.objects.filter(
            start_at__gte=current_month_start
        ).count()

        # Previous month
        prev_revenue = Payment.objects.filter(
            status='PAID',
            created_at__gte=prev_month_start,
            created_at__lte=prev_month_end
        ).aggregate(total=Sum('amount'))['total'] or 0

        prev_appointments = Appointment.objects.filter(
            start_at__gte=prev_month_start,
            start_at__lte=prev_month_end
        ).count()

        response = "📈 **Growth & Trend Analysis:**\n\n"

        # Revenue growth
        if prev_revenue > 0:
            revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
            response += f"**Revenue:**\n"
            response += f"Current: ₱{current_revenue:,.2f}\n"
            response += f"Previous: ₱{prev_revenue:,.2f}\n"
            if revenue_growth >= 0:
                response += f"📈 Growth: +{revenue_growth:.1f}%\n\n"
            else:
                response += f"📉 Decline: {revenue_growth:.1f}%\n\n"
        else:
            response += f"**Revenue:** ₱{current_revenue:,.2f}\n\n"

        # Appointment growth
        if prev_appointments > 0:
            appt_growth = ((current_appointments - prev_appointments) / prev_appointments) * 100
            response += f"**Appointments:**\n"
            response += f"Current: {current_appointments}\n"
            response += f"Previous: {prev_appointments}\n"
            if appt_growth >= 0:
                response += f"📈 Growth: +{appt_growth:.1f}%\n"
            else:
                response += f"📉 Decline: {appt_growth:.1f}%\n"
        else:
            response += f"**Appointments:** {current_appointments}\n"

        return response

    def get_profitability_analysis(self, message):
        """Analyze service profitability (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        services = Service.objects.annotate(
            bookings=Count('appointment', filter=Q(appointment__status='COMPLETED')),
            total_revenue=Sum('appointment__payment__amount',
                            filter=Q(appointment__payment__status='PAID'))
        ).filter(bookings__gt=0).order_by('-total_revenue')[:5]

        response = "💵 **Service Profitability Analysis:**\n\n"

        if services:
            response += "**Top 5 Most Profitable Services:**\n"
            for i, service in enumerate(services, 1):
                revenue = service.total_revenue or 0
                bookings = service.bookings or 0
                profit_per_booking = revenue / bookings if bookings > 0 else 0

                response += f"{i}. {service.name}\n"
                response += f"   Revenue: ₱{revenue:,.2f}\n"
                response += f"   Bookings: {bookings}\n"
                response += f"   Per Booking: ₱{profit_per_booking:,.2f}\n\n"
        else:
            response += "No profitability data yet.\n"

        return response

    def get_service_recommendations(self, message):
        """Provide intelligent service recommendations (staff/admin only)."""
        if not self.is_staff:
            return "Use customer feedback to recommend services!"

        # Get most popular services
        popular = Service.objects.annotate(
            bookings=Count('appointment', filter=Q(appointment__status='COMPLETED'))
        ).order_by('-bookings')[:3]

        response = "💡 **Service Recommendations:**\n\n"

        response += "**Top Recommended Services:**\n"
        for i, service in enumerate(popular, 1):
            response += f"{i}. **{service.name}**\n"
            response += f"   Price: ₱{service.price}\n"
            response += f"   Popular: {service.bookings} bookings\n\n"

        response += "💬 **Recommendation Strategy:**\n"
        response += "• Promote top services in marketing\n"
        response += "• Bundle slower-moving services with popular ones\n"
        response += "• Offer special packages during low-demand periods\n"

        return response

    def get_forecast_analysis(self, message):
        """Provide business forecast and predictions (staff/admin only)."""
        if not self.is_staff:
            return "This information is only available to staff members."

        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)

        recent_revenue = Payment.objects.filter(
            status='PAID',
            created_at__date__gte=last_7_days
        ).aggregate(total=Sum('amount'))['total'] or 0

        recent_appointments = Appointment.objects.filter(
            start_at__date__gte=last_7_days
        ).count()

        response = "🔮 **Business Forecast & Predictions:**\n\n"

        response += f"**Based on Last 7 Days:**\n"
        response += f"Average Daily Revenue: ₱{(recent_revenue / 7):,.2f}\n"
        response += f"Average Daily Appointments: {(recent_appointments / 7):.1f}\n\n"

        # Forecast for next 30 days
        projected_revenue = (recent_revenue / 7) * 30
        projected_appointments = (recent_appointments / 7) * 30

        response += f"**Projected Next 30 Days:**\n"
        response += f"💰 Est. Revenue: ₱{projected_revenue:,.2f}\n"
        response += f"📅 Est. Appointments: {projected_appointments:.0f}\n\n"

        response += "📊 **Trend Notes:**\n"
        response += "• Monitor actual vs projected performance\n"
        response += "• Adjust staffing based on forecast\n"
        response += "• Plan inventory for projected demand\n"

        return response
