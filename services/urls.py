from django.urls import path
from .views import (
    ServiceListView,
    ServiceDetailView,
    ServiceCreateView,
    ServiceUpdateView,
    ServiceDeleteView,
    ServiceArchiveView,
    ServiceUnarchiveView,
    ArchivedServicesListView,
    ServiceDownpaymentConfigView,
    PricingPlansView,
)

app_name = 'services'

urlpatterns = [
    path('', ServiceListView.as_view(), name='list'),
    path('pricing/', PricingPlansView.as_view(), name='pricing'),
    path('archived/', ArchivedServicesListView.as_view(), name='archived'),
    path('create/', ServiceCreateView.as_view(), name='create'),
    path('downpayment-config/', ServiceDownpaymentConfigView.as_view(), name='downpayment_config'),
    path('<int:pk>/', ServiceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ServiceUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ServiceDeleteView.as_view(), name='delete'),
    path('<int:pk>/archive/', ServiceArchiveView.as_view(), name='archive'),
    path('<int:pk>/unarchive/', ServiceUnarchiveView.as_view(), name='unarchive'),
]
