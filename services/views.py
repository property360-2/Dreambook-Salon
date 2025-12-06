from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.template.loader import render_to_string
from .models import Service, ServiceItem
from .forms import ServiceForm, ServiceItemFormSet
from core.mixins import StaffOrAdminRequiredMixin


class ServiceListView(ListView):
    """Public view listing all active services with search functionality."""

    model = Service
    template_name = 'pages/services_list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        """Only show active, non-archived services for customers. Show all for staff."""
        if self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']:
            qs = Service.objects.all().prefetch_related('service_items__item', 'features')
        else:
            qs = Service.objects.filter(is_active=True, is_archived=False).prefetch_related('service_items__item', 'features')

        # Add search filter (case-insensitive, partial match)
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Add sort functionality
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'price_asc':
            qs = qs.order_by('price')
        elif sort_by == 'price_desc':
            qs = qs.order_by('-price')
        elif sort_by == 'duration_asc':
            qs = qs.order_by('duration_minutes')
        elif sort_by == 'duration_desc':
            qs = qs.order_by('-duration_minutes')
        else:
            qs = qs.order_by('name')

        return qs

    def get_context_data(self, **kwargs):
        """Add search query and sort options to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        context['sort_by'] = self.request.GET.get('sort', 'name')
        return context

    def render_to_response(self, context, **response_kwargs):
        """Return JSON with rendered HTML when requested asynchronously."""
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(
                'components/organisms/services_results.html',
                context,
                request=self.request
            )
            count = context.get('paginator').count if context.get('paginator') else len(context.get('services', []))
            return JsonResponse({'html': html, 'count': count})
        return super().render_to_response(context, **response_kwargs)


class PricingPlansView(ListView):
    """Public view showing services in a pricing/plans layout."""

    model = Service
    template_name = 'pages/pricing_plans.html'
    context_object_name = 'services'
    paginate_by = None

    def get_queryset(self):
        """Only show active, non-archived services for non-staff, all services for staff."""
        if self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']:
            return Service.objects.all().prefetch_related('features').order_by('price')
        return Service.objects.filter(is_active=True, is_archived=False).prefetch_related('features').order_by('price')


class ServiceDetailView(DetailView):
    """Public view showing service details with inventory requirements."""

    model = Service
    template_name = 'pages/services_detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        """Only show active, non-archived services for non-staff, all for staff."""
        if self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']:
            return Service.objects.all().prefetch_related('service_items__item')
        return Service.objects.filter(is_active=True, is_archived=False).prefetch_related('service_items__item')

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

    def _appointments_qs(self):
        """Return all appointments linked to this service."""
        from appointments.models import Appointment

        return Appointment.objects.filter(service=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if service has any appointments
        appointments_qs = self._appointments_qs()
        context['has_appointments'] = appointments_qs.exists()
        context['appointment_count'] = appointments_qs.count()
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_name = self.object.name
        appointments_qs = self._appointments_qs()
        has_appointments = appointments_qs.exists()

        # Prevent deletion if service has appointments
        if has_appointments:
            appointment_count = appointments_qs.count()
            messages.error(
                request,
                f'❌ Cannot delete "{service_name}" - it has {appointment_count} customer appointment(s). Please cancel or complete all appointments first.'
            )
            return redirect(self.get_object().get_absolute_url())

        # Only delete if no appointments exist
        try:
            self.object.delete()
            messages.success(request, f'✓ Service "{service_name}" deleted successfully!')
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(
                request,
                f'❌ Cannot delete "{service_name}" - it is referenced by customer appointments.'
            )
            return redirect(self.get_object().get_absolute_url())


class ServiceArchiveView(StaffOrAdminRequiredMixin, UpdateView):
    """Staff/Admin view for archiving a service (soft delete)."""

    model = Service
    fields = []
    template_name = 'pages/services_confirm_archive.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'archive'
        return context

    def post(self, request, *args, **kwargs):
        from audit_log.models import AuditLog

        self.object = self.get_object()
        self.object.is_archived = True
        self.object.save()

        # Log archive action to audit trail
        AuditLog.log_action(
            user=request.user,
            action_type='SERVICE_ARCHIVE',
            description=f'Archived service "{self.object.name}"',
            obj=self.object,
            changes={'is_archived': {'before': False, 'after': True}},
            request=request
        )

        messages.success(
            request,
            f'✓ Service "{self.object.name}" has been archived and hidden from customers.'
        )
        return redirect(self.success_url)


class ServiceUnarchiveView(StaffOrAdminRequiredMixin, UpdateView):
    """Staff/Admin view for unarchiving a service (restore from soft delete)."""

    model = Service
    fields = []
    template_name = 'pages/services_confirm_archive.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'restore'
        return context

    def post(self, request, *args, **kwargs):
        from audit_log.models import AuditLog

        self.object = self.get_object()
        self.object.is_archived = False
        self.object.save()

        # Log unarchive action to audit trail
        AuditLog.log_action(
            user=request.user,
            action_type='SERVICE_UNARCHIVE',
            description=f'Restored service "{self.object.name}"',
            obj=self.object,
            changes={'is_archived': {'before': True, 'after': False}},
            request=request
        )

        messages.success(
            request,
            f'✓ Service "{self.object.name}" has been restored and is now visible to customers.'
        )
        return redirect(self.success_url)


class ArchivedServicesListView(StaffOrAdminRequiredMixin, ListView):
    """Staff/Admin view to see all archived services."""

    model = Service
    template_name = 'pages/services_archived.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        """Show only archived services."""
        return Service.objects.filter(is_archived=True).order_by('-updated_at')


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
