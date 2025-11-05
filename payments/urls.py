from django.urls import path
from .views import (
    PaymentInitiateView,
    PaymentDetailView,
    PaymentListView,
    PaymentRetryView,
    PaymentStatsView,
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListView.as_view(), name='list'),
    path('stats/', PaymentStatsView.as_view(), name='stats'),
    path('initiate/<int:appointment_id>/', PaymentInitiateView.as_view(), name='initiate'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='detail'),
    path('<int:pk>/retry/', PaymentRetryView.as_view(), name='retry'),
]
