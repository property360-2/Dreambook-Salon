from django.urls import path
from .views import (
    PaymentInitiateView,
    PaymentDetailView,
    PaymentListView,
    PaymentRetryView,
    PaymentStatsView,
    PaymentConfirmationView,
    GenerateReceiptView,
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListView.as_view(), name='list'),
    path('stats/', PaymentStatsView.as_view(), name='stats'),
    path('initiate/<int:appointment_id>/', PaymentInitiateView.as_view(), name='initiate'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='detail'),
    path('<int:pk>/retry/', PaymentRetryView.as_view(), name='retry'),
    path('<int:payment_id>/confirmation/', PaymentConfirmationView.as_view(), name='confirmation'),
    path('<int:payment_id>/download-receipt/', GenerateReceiptView.as_view(), name='generate_receipt'),
]
