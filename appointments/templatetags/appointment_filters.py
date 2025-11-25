"""
Template filters for customer-friendly appointment status display.
"""
from django import template

register = template.Library()


@register.filter
def customer_friendly_status(status):
    """
    Convert technical appointment status to customer-friendly display.

    Args:
        status: The appointment status value (confirmed, in_progress, etc.)

    Returns:
        str: Customer-friendly status label
    """
    if status in ['confirmed', 'in_progress']:
        return 'Active'
    elif status == 'completed':
        return 'Completed'
    elif status in ['cancelled', 'no_show']:
        return 'Cancelled'
    elif status == 'pending':
        return 'Pending'
    return status.title()


@register.filter
def customer_status_badge_class(status):
    """
    Return CSS badge class for customer-friendly status display.

    Args:
        status: The appointment status value

    Returns:
        str: CSS class for badge styling
    """
    if status in ['confirmed', 'in_progress']:
        return 'badge-primary'  # Blue/gold for active appointments
    elif status == 'completed':
        return 'badge-success'  # Green for completed
    elif status in ['cancelled', 'no_show']:
        return 'badge-danger'  # Red for cancelled
    elif status == 'pending':
        return 'badge-warning'  # Yellow/orange for pending
    return 'badge-secondary'  # Gray for unknown


@register.filter
def staff_status_badge_class(status):
    """
    Return CSS badge class for staff view (more detailed status colors).

    Args:
        status: The appointment status value

    Returns:
        str: CSS class for badge styling
    """
    status_classes = {
        'pending': 'badge-warning',
        'confirmed': 'badge-primary',
        'in_progress': 'badge-info',
        'completed': 'badge-success',
        'cancelled': 'badge-danger',
        'no_show': 'badge-secondary',
    }
    return status_classes.get(status, 'badge-secondary')
