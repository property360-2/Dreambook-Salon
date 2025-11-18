"""
Utility functions for appointment management.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from .models import Appointment


def get_calendar_data(year, month, user=None, is_staff=False):
    """
    Generate calendar data with appointment counts for each day.

    Args:
        year: Calendar year (int)
        month: Calendar month (1-12) (int)
        user: User object for customer-specific appointments (optional)
        is_staff: Boolean to show all appointments (staff/admin only)

    Returns:
        dict with:
            - year, month: Calendar identifiers
            - days: List of day dicts with date, day_num, appointment_count, appointments
            - appointment_details: Dict mapping dates to appointment lists
    """
    from calendar import monthrange, month_name

    # Get calendar structure
    num_days = monthrange(year, month)[1]
    first_weekday = monthrange(year, month)[0]  # 0=Monday, 6=Sunday

    # Build base query
    if user and not is_staff:
        # Customer: only their appointments
        query = Appointment.objects.filter(customer=user)
    else:
        # Staff/Admin: all appointments
        query = Appointment.objects.all()

    # Get appointments for the month
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, num_days, 23, 59, 59)

    appointments_qs = query.filter(
        start_at__date__gte=month_start.date(),
        start_at__date__lte=month_end.date()
    ).select_related('service', 'customer').order_by('start_at')

    # Group appointments by date
    appointments_by_date = {}
    for appt in appointments_qs:
        date_key = appt.start_at.date().isoformat()
        if date_key not in appointments_by_date:
            appointments_by_date[date_key] = []
        appointments_by_date[date_key].append(appt)

    # Build calendar days
    days = []

    # Add empty days from previous month
    for _ in range(first_weekday):
        days.append({
            'date': None,
            'day_num': None,
            'is_current_month': False,
            'appointment_count': 0,
            'appointments': [],
            'has_pending': False,
        })

    # Add days of current month
    for day_num in range(1, num_days + 1):
        date_obj = datetime(year, month, day_num)
        date_key = date_obj.date().isoformat()

        appts = appointments_by_date.get(date_key, [])

        # Check if any appointments are pending/confirmed
        has_pending = any(
            appt.status in [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
            for appt in appts
        )

        days.append({
            'date': date_key,
            'date_obj': date_obj.date(),
            'day_num': day_num,
            'is_current_month': True,
            'is_today': date_obj.date() == timezone.now().date(),
            'appointment_count': len(appts),
            'appointments': appts,
            'has_pending': has_pending,
        })

    return {
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'days': days,
        'appointment_details': appointments_by_date,
    }


def get_month_appointments(year, month, user=None):
    """
    Get all appointments for a specific month.

    Args:
        year: Calendar year (int)
        month: Calendar month (1-12) (int)
        user: User object for customer-specific appointments (optional)

    Returns:
        QuerySet of Appointment objects
    """
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1) - timedelta(days=1)

    query = Appointment.objects.select_related('service', 'customer')

    if user:
        query = query.filter(customer=user)

    return query.filter(
        start_at__date__gte=month_start.date(),
        start_at__date__lte=month_end.date()
    ).order_by('start_at')


def get_day_appointments(year, month, day, user=None):
    """
    Get all appointments for a specific day.

    Args:
        year, month, day: Date components (int)
        user: User object for customer-specific appointments (optional)

    Returns:
        QuerySet of Appointment objects for that day
    """
    date_obj = datetime(year, month, day)
    day_start = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)

    query = Appointment.objects.select_related('service', 'customer')

    if user:
        query = query.filter(customer=user)

    return query.filter(
        start_at__gte=day_start,
        start_at__lte=day_end
    ).order_by('start_at')
