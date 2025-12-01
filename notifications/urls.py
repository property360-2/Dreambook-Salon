from django.urls import path
from .views import (
    get_notifications_api,
    get_unread_count_api,
    mark_as_read_api,
    delete_notification_api,
    mark_all_as_read_api,
)

app_name = 'notifications'

urlpatterns = [
    path('api/list/', get_notifications_api, name='api_list'),
    path('api/unread-count/', get_unread_count_api, name='api_unread_count'),
    path('api/mark-read/', mark_as_read_api, name='api_mark_read'),
    path('api/delete/', delete_notification_api, name='api_delete'),
    path('api/mark-all-read/', mark_all_as_read_api, name='api_mark_all_read'),
]
