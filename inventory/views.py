from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, F
from core.mixins import StaffOrAdminRequiredMixin
from .models import Item
from .forms import ItemForm, RestockForm, AdjustStockForm


class InventoryListView(StaffOrAdminRequiredMixin, ListView):
    """Staff/Admin view to list all inventory items."""

    model = Item
    template_name = 'pages/inventory_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        """Show all items with filters."""
        qs = Item.objects.all().order_by('name')

        # Filter by stock status
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'low':
            qs = qs.filter(stock__lte=F('threshold'), stock__gt=0)
        elif stock_status == 'out':
            qs = qs.filter(stock=0)
        elif stock_status == 'in':
            qs = qs.filter(stock__gt=F('threshold'))

        # Search by name
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_status'] = self.request.GET.get('stock_status', '')
        context['search'] = self.request.GET.get('search', '')

        # Stock counts
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


class InventoryDetailView(StaffOrAdminRequiredMixin, DetailView):
    """Staff/Admin view to see item details and services using it."""

    model = Item
    template_name = 'pages/inventory_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get services that use this item
        item = self.get_object()
        context['services_using_item'] = item.service_links.select_related('service').all()
        context['restock_form'] = RestockForm()
        return context


class InventoryCreateView(StaffOrAdminRequiredMixin, CreateView):
    """Staff/Admin view for creating new inventory items."""

    model = Item
    form_class = ItemForm
    template_name = 'pages/inventory_form.html'
    success_url = reverse_lazy('inventory:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Inventory Item'
        context['submit_text'] = 'Create Item'
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Inventory item "{form.instance.name}" created successfully!'
        )
        return super().form_valid(form)


class InventoryUpdateView(StaffOrAdminRequiredMixin, UpdateView):
    """Staff/Admin view for editing inventory items."""

    model = Item
    form_class = ItemForm
    template_name = 'pages/inventory_form.html'
    success_url = reverse_lazy('inventory:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Item: {self.object.name}'
        context['submit_text'] = 'Update Item'
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Inventory item "{form.instance.name}" updated successfully!'
        )
        return super().form_valid(form)


class InventoryDeleteView(StaffOrAdminRequiredMixin, DeleteView):
    """Staff/Admin view for deleting inventory items."""

    model = Item
    template_name = 'pages/inventory_confirm_delete.html'
    success_url = reverse_lazy('inventory:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if item is used in any services
        context['used_in_services'] = self.object.service_links.exists()
        context['service_count'] = self.object.service_links.count()
        context['services'] = self.object.service_links.select_related('service').all()[:5]
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        item_name = self.object.name

        # If item is used in services, deactivate instead of delete
        if self.object.service_links.exists():
            self.object.is_active = False
            self.object.save()
            messages.warning(
                request,
                f'Item "{item_name}" has been deactivated (used in services).'
            )
        else:
            self.object.delete()
            messages.success(request, f'Item "{item_name}" deleted successfully!')

        return redirect(self.success_url)


class InventoryRestockView(StaffOrAdminRequiredMixin, View):
    """Restock inventory items (add quantity)."""

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        form = RestockForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']

            # Add to stock
            item.stock += quantity
            item.save()

            message = f"Successfully restocked {quantity} {item.unit}. New stock: {item.stock} {item.unit}"
            if notes:
                message += f" (Notes: {notes})"
            messages.success(request, message)
        else:
            messages.error(request, "Invalid restock quantity.")

        return redirect('inventory:detail', pk=pk)


class InventoryAdjustView(StaffOrAdminRequiredMixin, View):
    """Adjust inventory stock (add or remove)."""

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        try:
            adjustment = float(request.POST.get('adjustment', 0))
            reason = request.POST.get('reason', '').strip()

            if adjustment == 0:
                messages.warning(request, "No adjustment made (adjustment is 0)")
                return redirect('inventory:list')

            # Calculate new stock
            new_stock = item.stock + adjustment

            if new_stock < 0:
                messages.error(request, f"Cannot adjust: would result in negative stock ({new_stock})")
                return redirect('inventory:list')

            # Update stock
            item.stock = new_stock
            item.save()

            adjustment_type = "added" if adjustment > 0 else "removed"
            message = f"Successfully {adjustment_type} {abs(adjustment)} {item.unit}. New stock: {item.stock} {item.unit}"
            if reason:
                message += f" (Reason: {reason})"

            messages.success(request, message)

        except (ValueError, TypeError):
            messages.error(request, "Invalid adjustment value")

        return redirect('inventory:list')


class LowStockAlertsView(StaffOrAdminRequiredMixin, ListView):
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
