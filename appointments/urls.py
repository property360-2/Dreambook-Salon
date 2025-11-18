from django.urls import path
from .views import (
    AppointmentBookingView,
    MyAppointmentsView,
    AppointmentDetailView,
    AppointmentCancelView,
    StaffAppointmentListView,
    AppointmentCompleteView,
    AppointmentUpdateStatusView,
    CheckSlotAvailabilityView,
)

app_name = 'appointments'

urlpatterns = [
    # Customer views
    path('book/', AppointmentBookingView.as_view(), name='book'),
    path('my/', MyAppointmentsView.as_view(), name='my_appointments'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='detail'),
    path('<int:pk>/cancel/', AppointmentCancelView.as_view(), name='cancel'),

    # API endpoints
    path('api/check-availability/', CheckSlotAvailabilityView.as_view(), name='check_availability'),

    # Staff/Admin views
    path('staff/', StaffAppointmentListView.as_view(), name='staff_list'),
    path('<int:pk>/complete/', AppointmentCompleteView.as_view(), name='complete'),
    path('<int:pk>/update-status/', AppointmentUpdateStatusView.as_view(), name='update_status'),
]
