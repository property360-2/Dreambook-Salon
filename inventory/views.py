from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, F
from core.mixins import StaffOrAdminRequiredMixin
from .models import Item


class InventoryListView(LoginRequiredMixin, StaffOrAdminRequiredMixin, ListView):
    """Staff/Admin view to list all inventory items."""

    model = Item
    template_name = 'pages/inventory_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        """Show all items with filters."""
        qs = Item.objects.all().order_by('name')

        # Filter by stock status
        status_filter = self.request.GET.get('status')
        if status_filter == 'low':
            qs = qs.filter(stock__lte=F('threshold'))
        elif status_filter == 'out':
            qs = qs.filter(stock=0)
        elif status_filter == 'in_stock':
            qs = qs.filter(stock__gt=F('threshold'))

        # Search by name
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')

        # Low stock alerts count
        context['low_stock_count'] = Item.objects.filter(
            is_active=True,
            stock__lte=F('threshold'),
            stock__gt=0
        ).count()

        context['out_of_stock_count'] = Item.objects.filter(
            is_active=True,
            stock=0
        ).count()

        return context


class InventoryDetailView(LoginRequiredMixin, StaffOrAdminRequiredMixin, DetailView):
    """Staff/Admin view to see item details and services using it."""

    model = Item
    template_name = 'pages/inventory_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get services that use this item
        item = self.get_object()
        context['services_using_item'] = item.service_links.select_related('service').all()
        return context


class InventoryAdjustView(LoginRequiredMixin, StaffOrAdminRequiredMixin, View):
    """Adjust inventory stock (add or remove)."""

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        try:
            adjustment = float(request.POST.get('adjustment', 0))
            reason = request.POST.get('reason', '').strip()

            if adjustment == 0:
                messages.warning(request, "No adjustment made (adjustment is 0)")
                return redirect('inventory:detail', pk=pk)

            # Calculate new stock
            new_stock = item.stock + adjustment

            if new_stock < 0:
                messages.error(request, f"Cannot adjust: would result in negative stock ({new_stock})")
                return redirect('inventory:detail', pk=pk)

            # Update stock
            item.stock = new_stock
            item.save()

            adjustment_type = "added" if adjustment > 0 else "removed"
            messages.success(
                request,
                f"Successfully {adjustment_type} {abs(adjustment)} {item.unit}. New stock: {item.stock} {item.unit}"
            )

        except (ValueError, TypeError):
            messages.error(request, "Invalid adjustment value")

        return redirect('inventory:detail', pk=pk)


class LowStockAlertsView(LoginRequiredMixin, StaffOrAdminRequiredMixin, ListView):
    """View showing items with low or out of stock."""

    model = Item
    template_name = 'pages/inventory_alerts.html'
    context_object_name = 'items'

    def get_queryset(self):
        """Show only low stock or out of stock items."""
        return Item.objects.filter(
            is_active=True,
            stock__lte=F('threshold')
        ).order_by('stock', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Separate critical (out of stock) from low stock
        items = self.get_queryset()
        context['out_of_stock'] = items.filter(stock=0)
        context['low_stock'] = items.filter(stock__gt=0)

        return context
