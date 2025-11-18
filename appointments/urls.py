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
    SlotLimitListView,
    SlotLimitCreateView,
    SlotLimitUpdateView,
    SlotLimitDeleteView,
    SlotLimitDetailView,
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

    # Slot Limit Management views
    path('slot-limits/', SlotLimitListView.as_view(), name='slotlimit_list'),
    path('slot-limits/add/', SlotLimitCreateView.as_view(), name='slotlimit_create'),
    path('slot-limits/<int:pk>/', SlotLimitDetailView.as_view(), name='slotlimit_detail'),
    path('slot-limits/<int:pk>/edit/', SlotLimitUpdateView.as_view(), name='slotlimit_edit'),
    path('slot-limits/<int:pk>/delete/', SlotLimitDeleteView.as_view(), name='slotlimit_delete'),
]
