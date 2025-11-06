from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Service


class ServiceListView(ListView):
    """Public view listing all active services."""

    model = Service
    template_name = 'pages/services_list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        """Only show active services."""
        return Service.objects.filter(is_active=True).prefetch_related('service_items__item')


class ServiceDetailView(DetailView):
    """Public view showing service details with inventory requirements."""

    model = Service
    template_name = 'pages/services_detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        """Only show active services."""
        return Service.objects.filter(is_active=True).prefetch_related('service_items__item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if service has sufficient inventory
        service = self.get_object()
        sufficient_stock = True
        required_items = []

        for service_item in service.service_items.all():
            item = service_item.item
            required_items.append({
                'name': item.name,
                'required': service_item.qty_per_service,
                'available': item.stock,
                'unit': item.unit,
                'sufficient': item.stock >= service_item.qty_per_service
            })
            if item.stock < service_item.qty_per_service:
                sufficient_stock = False

        context['required_items'] = required_items
        context['sufficient_stock'] = sufficient_stock
        return context
