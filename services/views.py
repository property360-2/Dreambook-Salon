from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Service, ServiceItem
from .forms import ServiceForm, ServiceItemFormSet
from core.mixins import StaffOrAdminRequiredMixin


class ServiceListView(ListView):
    """Public view listing all active services."""

    model = Service
    template_name = 'pages/services_list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        """Only show active services for non-staff, all services for staff."""
        if self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']:
            return Service.objects.all().prefetch_related('service_items__item')
        return Service.objects.filter(is_active=True).prefetch_related('service_items__item')


class ServiceDetailView(DetailView):
    """Public view showing service details with inventory requirements."""

    model = Service
    template_name = 'pages/services_detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        """Only show active services for non-staff, all for staff."""
        if self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']:
            return Service.objects.all().prefetch_related('service_items__item')
        return Service.objects.filter(is_active=True).prefetch_related('service_items__item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get required inventory items
        context['required_inventory'] = self.object.service_items.select_related('item').all()
        return context


class ServiceCreateView(StaffOrAdminRequiredMixin, CreateView):
    """Staff/Admin view for creating new services."""

    model = Service
    form_class = ServiceForm
    template_name = 'pages/services_form.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ServiceItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ServiceItemFormSet(instance=self.object)
        context['form_title'] = 'Create New Service'
        context['submit_text'] = 'Create Service'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                messages.success(
                    self.request,
                    f'Service "{self.object.name}" created successfully!'
                )
                return redirect(self.success_url)
            else:
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ServiceUpdateView(StaffOrAdminRequiredMixin, UpdateView):
    """Staff/Admin view for editing existing services."""

    model = Service
    form_class = ServiceForm
    template_name = 'pages/services_form.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ServiceItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ServiceItemFormSet(instance=self.object)
        context['form_title'] = f'Edit Service: {self.object.name}'
        context['submit_text'] = 'Update Service'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                messages.success(
                    self.request,
                    f'Service "{self.object.name}" updated successfully!'
                )
                return redirect(self.success_url)
            else:
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ServiceDeleteView(StaffOrAdminRequiredMixin, DeleteView):
    """Staff/Admin view for deleting services."""

    model = Service
    template_name = 'pages/services_confirm_delete.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if service has any appointments
        context['has_appointments'] = self.object.appointment_set.exists()
        context['appointment_count'] = self.object.appointment_set.count()
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_name = self.object.name

        # Instead of hard delete, we can soft delete by setting is_active=False
        if self.object.appointment_set.exists():
            self.object.is_active = False
            self.object.save()
            messages.warning(
                request,
                f'Service "{service_name}" has been deactivated (has existing appointments).'
            )
        else:
            self.object.delete()
            messages.success(request, f'Service "{service_name}" deleted successfully!')

        return redirect(self.success_url)


class ServiceDownpaymentConfigView(StaffOrAdminRequiredMixin, TemplateView):
    """Admin view for managing downpayment configuration per service."""

    template_name = 'pages/service_downpayment_config.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all services
        services = Service.objects.filter(is_active=True).order_by('name')
        context['services'] = services

        # Get current active GCash QR code
        from payments.models import GCashQRCode
        context['current_qr'] = GCashQRCode.get_active_qr()

        return context

    def post(self, request, *args, **kwargs):
        """Handle both GCash QR upload and downpayment settings."""
        from payments.models import GCashQRCode

        # Check if this is a GCash QR upload
        if 'qr_image' in request.FILES:
            try:
                qr_file = request.FILES['qr_image']

                # Create or update GCash QR code
                qr = GCashQRCode.objects.create(
                    qr_image=qr_file,
                    description='GCash Receive Payment',
                    is_active=True
                )

                # Deactivate other QR codes
                GCashQRCode.objects.exclude(pk=qr.pk).update(is_active=False)

                return JsonResponse({
                    'success': True,
                    'message': 'GCash QR code uploaded successfully'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)

        # Otherwise handle downpayment settings update
        service_id = request.POST.get('service_id')
        requires_downpayment = request.POST.get('requires_downpayment') == 'true'
        downpayment_amount = request.POST.get('downpayment_amount', '0')

        try:
            service = Service.objects.get(id=service_id)
            service.requires_downpayment = requires_downpayment

            # Only set amount if downpayment is required
            if requires_downpayment:
                service.downpayment_amount = float(downpayment_amount)
            else:
                service.downpayment_amount = 0

            service.save()

            return JsonResponse({
                'success': True,
                'message': f'Updated {service.name} successfully'
            })
        except Service.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Service not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
