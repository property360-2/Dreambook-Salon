from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Notification


@login_required
@require_http_methods(["GET"])
def get_notifications_api(request):
    """API endpoint to get user's notifications."""

    user = request.user
    unread_only = request.GET.get('unread', 'false').lower() == 'true'
    page = request.GET.get('page', 1)

    # Get notifications
    if unread_only:
        notifications = user.notifications.filter(is_read=False)
    else:
        notifications = user.notifications.all()

    # Paginate
    paginator = Paginator(notifications, 10)
    page_obj = paginator.get_page(page)

    # Build response
    data = {
        'count': paginator.count,
        'unread_count': user.notifications.filter(is_read=False).count(),
        'notifications': [
            {
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'is_read': notif.is_read,
                'link': notif.link,
                'created_at': notif.created_at.isoformat(),
            }
            for notif in page_obj
        ]
    }

    return JsonResponse(data)


@login_required
@require_http_methods(["GET"])
def get_unread_count_api(request):
    """API endpoint to get unread notification count."""

    unread_count = request.user.notifications.filter(is_read=False).count()

    return JsonResponse({
        'unread_count': unread_count
    })


@login_required
@require_POST
def mark_as_read_api(request):
    """API endpoint to mark a notification as read."""

    notification_id = request.POST.get('notification_id')

    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': request.user.notifications.filter(is_read=False).count()
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)


@login_required
@require_POST
def delete_notification_api(request):
    """API endpoint to delete a notification."""

    notification_id = request.POST.get('notification_id')

    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.delete()

        return JsonResponse({
            'success': True,
            'message': 'Notification deleted',
            'unread_count': request.user.notifications.filter(is_read=False).count()
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)


@login_required
@require_POST
def mark_all_as_read_api(request):
    """API endpoint to mark all notifications as read."""

    request.user.notifications.filter(is_read=False).update(is_read=True)

    return JsonResponse({
        'success': True,
        'message': 'All notifications marked as read',
        'unread_count': 0
    })
