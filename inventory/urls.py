from django.urls import path
from .views import (
    InventoryListView,
    InventoryDetailView,
    InventoryCreateView,
    InventoryUpdateView,
    InventoryDeleteView,
    InventoryRestockView,
    InventoryAdjustView,
    LowStockAlertsView,
)

app_name = 'inventory'

urlpatterns = [
    path('', InventoryListView.as_view(), name='list'),
    path('create/', InventoryCreateView.as_view(), name='create'),
    path('alerts/', LowStockAlertsView.as_view(), name='alerts'),
    path('<int:pk>/', InventoryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', InventoryUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', InventoryDeleteView.as_view(), name='delete'),
    path('<int:pk>/restock/', InventoryRestockView.as_view(), name='restock'),
    path('<int:pk>/adjust/', InventoryAdjustView.as_view(), name='adjust'),
]
