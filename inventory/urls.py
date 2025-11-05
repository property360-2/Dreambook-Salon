from django.urls import path
from .views import (
    InventoryListView,
    InventoryDetailView,
    InventoryAdjustView,
    LowStockAlertsView,
)

app_name = 'inventory'

urlpatterns = [
    path('', InventoryListView.as_view(), name='list'),
    path('alerts/', LowStockAlertsView.as_view(), name='alerts'),
    path('<int:pk>/', InventoryDetailView.as_view(), name='detail'),
    path('<int:pk>/adjust/', InventoryAdjustView.as_view(), name='adjust'),
]
