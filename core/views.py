from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, datetime
import json

from .forms import CustomerRegistrationForm, EmailAuthenticationForm, UserManagementForm
from .mixins import StaffOrAdminRequiredMixin
from .models import User
from appointments.models import Appointment
from appointments.utils import get_calendar_data
from payments.models import Payment
from inventory.models import Item
from services.models import Service


class HomeView(TemplateView):
    """Landing page - routes to dashboard for staff/admin, business page for others."""
    template_name = "pages/home.html"

    def dispatch(self, request, *args, **kwargs):
        # Redirect staff/admin to dashboard
        if request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get actual featured services from database
        featured_services = Service.objects.filter(is_active=True)[:3]
        context['featured_services'] = featured_services

        return context


class DashboardView(StaffOrAdminRequiredMixin, TemplateView):
    """Comprehensive dashboard for admin and staff with all business metrics."""
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date ranges
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # === REVENUE STATS ===
        all_payments = Payment.objects.filter(status=Payment.Status.PAID)

        context['total_revenue'] = all_payments.aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_today'] = all_payments.filter(
            created_at__gte=today_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_week'] = all_payments.filter(
            created_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_month'] = all_payments.filter(
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

        # === APPOINTMENT STATS ===
        all_appointments = Appointment.objects.all()

        context['total_appointments'] = all_appointments.count()
        context['completed_appointments'] = all_appointments.filter(
            status=Appointment.Status.COMPLETED
        ).count()
        context['pending_appointments'] = all_appointments.filter(
            status=Appointment.Status.PENDING
        ).count()
        context['confirmed_appointments'] = all_appointments.filter(
            status=Appointment.Status.CONFIRMED
        ).count()
        context['cancelled_appointments'] = all_appointments.filter(
            status=Appointment.Status.CANCELLED
        ).count()

        # Upcoming appointments (today and future)
        context['upcoming_appointments'] = all_appointments.filter(
            start_at__gte=now,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).order_by('start_at')[:5]

        # Today's appointments
        tomorrow_start = today_start + timedelta(days=1)
        context['today_appointments'] = all_appointments.filter(
            start_at__gte=today_start,
            start_at__lt=tomorrow_start
        ).order_by('start_at')

        # === SERVICES STATS ===
        context['total_services'] = Service.objects.filter(is_active=True).count()
        context['inactive_services'] = Service.objects.filter(is_active=False).count()

        # Top services by bookings
        top_services = Service.objects.annotate(
            booking_count=Count('appointments'),
            completed_count=Count('appointments', filter=Q(appointments__status=Appointment.Status.COMPLETED)),
            revenue=Sum('appointments__payments__amount', filter=Q(appointments__payments__status=Payment.Status.PAID))
        ).order_by('-booking_count')[:5]
        context['top_services'] = top_services

        # === INVENTORY STATS ===
        all_items = Item.objects.filter(is_active=True)
        context['total_inventory_items'] = all_items.count()

        low_stock_items = all_items.filter(stock__lte=F('threshold')).order_by('stock')
        context['low_stock_items'] = low_stock_items[:5]
        context['low_stock_count'] = low_stock_items.count()
        context['out_of_stock_count'] = all_items.filter(stock=0).count()

        # === PAYMENT STATS ===
        context['total_payments'] = all_payments.count()
        context['pending_payments'] = Payment.objects.filter(status=Payment.Status.PENDING).count()

        # Payment method breakdown
        payment_by_method = []
        for method_key, method_label in Payment.Method.choices:
            count = all_payments.filter(method=method_key).count()
            revenue = all_payments.filter(method=method_key).aggregate(
                total=Sum('amount')
            )['total'] or 0
            if count > 0:
                payment_by_method.append({
                    'method': method_label,
                    'count': count,
                    'revenue': revenue
                })
        context['payment_by_method'] = payment_by_method

        # === RECENT ACTIVITY ===
        context['recent_appointments'] = Appointment.objects.select_related(
            'service', 'customer'
        ).order_by('-created_at')[:5]

        context['recent_payments'] = Payment.objects.select_related(
            'appointment', 'appointment__service'
        ).order_by('-created_at')[:5]

        # === CALENDAR DATA ===
        year = int(self.request.GET.get('year', now.year))
        month = int(self.request.GET.get('month', now.month))

        calendar_data = get_calendar_data(year, month, user=None, is_staff=True)
        context['calendar'] = calendar_data
        context['current_year'] = year
        context['current_month'] = month

        # Get previous and next month for navigation
        if month == 1:
            context['prev_month'] = 12
            context['prev_year'] = year - 1
        else:
            context['prev_month'] = month - 1
            context['prev_year'] = year

        if month == 12:
            context['next_month'] = 1
            context['next_year'] = year + 1
        else:
            context['next_month'] = month + 1
            context['next_year'] = year

        return context


class EmailLoginView(LoginView):
    template_name = "pages/auth_login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "You're signed in. Welcome back!")
        # Avoid middleware double-logging; we'll capture a structured LOGIN entry here
        self.request.audit_log_skip = True
        response = super().form_valid(form)

        AuditLog.log_action(
            user=self.request.user,
            action_type='LOGIN',
            description="User signed in via email/password",
            request=self.request,
            status_code=getattr(response, "status_code", None),
            source="APPLICATION",
            metadata={"auth_via": "email_login"},
        )
        return response


class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("core:login")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You've been signed out.")
        actor = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        request.audit_log_skip = True

        response = super().dispatch(request, *args, **kwargs)

        if actor:
            AuditLog.log_action(
                user=actor,
                action_type='LOGOUT',
                description="User signed out",
                request=request,
                status_code=getattr(response, "status_code", None),
                source="APPLICATION",
                metadata={"auth_via": "logout_view"},
            )

        return response


class CustomerRegistrationView(FormView):
    template_name = "pages/auth_register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Welcome aboard! You're now signed in.")
        return super().form_valid(form)


# ===== USER MANAGEMENT VIEWS (Manager/Admin Only) =====

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from .forms import UserManagementForm
from audit_log.models import AuditLog


class UserManagementListView(StaffOrAdminRequiredMixin, ListView):
    """List all users for management"""
    model = User
    template_name = 'pages/user_management_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        """Filter users based on search"""
        queryset = User.objects.all().order_by('-date_joined')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        role_filter = self.request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.Roles.choices
        context['search'] = self.request.GET.get('search', '')
        context['selected_role'] = self.request.GET.get('role', '')
        return context


class UserCreateView(StaffOrAdminRequiredMixin, CreateView):
    """Create new user"""
    model = User
    template_name = 'pages/user_management_form.html'
    form_class = UserManagementForm
    success_url = reverse_lazy('core:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the action
        self.request.audit_log_skip = True
        AuditLog.log_action(
            user=self.request.user,
            action_type='USER_CREATE',
            description=f"Created user {form.instance.email} with role {form.instance.role}",
            obj=form.instance,
            request=self.request
        )
        messages.success(self.request, f"User {form.instance.email} created successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        context['roles'] = User.Roles.choices
        return context


class UserUpdateView(StaffOrAdminRequiredMixin, UpdateView):
    """Update user details and role"""
    model = User
    template_name = 'pages/user_management_form.html'
    form_class = UserManagementForm
    success_url = reverse_lazy('core:user_list')

    def form_valid(self, form):
        # Track changes
        changes = {}
        original = User.objects.get(pk=self.object.pk)

        if original.role != form.cleaned_data['role']:
            changes['role'] = {
                'before': original.get_role_display(),
                'after': form.cleaned_data['role']
            }

        if original.first_name != form.cleaned_data.get('first_name'):
            changes['first_name'] = {
                'before': original.first_name,
                'after': form.cleaned_data.get('first_name')
            }

        response = super().form_valid(form)

        # Log the action
        if changes:
            self.request.audit_log_skip = True
            AuditLog.log_action(
                user=self.request.user,
                action_type='USER_UPDATE',
                description=f"Updated user {form.instance.email}",
                obj=form.instance,
                changes=changes,
                request=self.request
            )

        messages.success(self.request, f"User {form.instance.email} updated successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User: {self.object.email}'
        context['roles'] = User.Roles.choices
        context['is_edit'] = True
        return context


class UserDetailView(StaffOrAdminRequiredMixin, DetailView):
    """View user details and activity"""
    model = User
    template_name = 'pages/user_management_detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user's audit logs
        user_actions = AuditLog.objects.filter(
            user=self.object
        ).order_by('-timestamp')[:20]
        context['user_actions'] = user_actions
        context['total_actions'] = AuditLog.objects.filter(user=self.object).count()
        return context


class UserDeactivateView(StaffOrAdminRequiredMixin, DetailView):
    """Deactivate user account"""
    model = User
    template_name = 'pages/user_management_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_type'] = 'deactivate'
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()

        request.audit_log_skip = True
        AuditLog.log_action(
            user=request.user,
            action_type='USER_DEACTIVATE',
            description=f"Deactivated user {user.email}",
            obj=user,
            request=request
        )

        messages.warning(request, f"User {user.email} has been deactivated.")
        return HttpResponseRedirect(reverse_lazy('core:user_list'))


class UserReactivateView(StaffOrAdminRequiredMixin, DetailView):
    """Reactivate deactivated user account"""
    model = User
    template_name = 'pages/user_management_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_type'] = 'reactivate'
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = True
        user.save()

        request.audit_log_skip = True
        AuditLog.log_action(
            user=request.user,
            action_type='USER_REACTIVATE',
            description=f"Reactivated user {user.email}",
            obj=user,
            request=request
        )

        messages.success(request, f"User {user.email} has been reactivated.")
        return HttpResponseRedirect(reverse_lazy('core:user_list'))


class UserResetPasswordView(StaffOrAdminRequiredMixin, DetailView):
    """Send password reset link to user"""
    model = User
    template_name = 'pages/user_management_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_type'] = 'reset_password'
        return context

    def post(self, request, *args, **kwargs):
        from django.contrib.auth.tokens import default_token_generator
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        user = self.get_object()

        # Generate password reset token
        token = default_token_generator.make_token(user)

        # Create reset URL (you'll need to add this to your URL config)
        reset_url = request.build_absolute_uri(
            reverse_lazy('password_reset_confirm', kwargs={'uidb64': user.pk, 'token': token})
        )

        # Log the action
        request.audit_log_skip = True
        AuditLog.log_action(
            user=request.user,
            action_type='PASSWORD_RESET',
            description=f"Password reset initiated for {user.email}",
            obj=user,
            request=request
        )

        messages.info(request, f"Password reset link sent to {user.email}")
        return HttpResponseRedirect(reverse_lazy('core:user_list'))


class UserDeleteView(StaffOrAdminRequiredMixin, DeleteView):
    """Permanently delete user account (admin only)"""
    model = User
    template_name = 'pages/user_management_confirm_delete.html'
    success_url = reverse_lazy('core:user_list')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        email = user.email

        # Log before deletion
        request.audit_log_skip = True
        AuditLog.log_action(
            user=request.user,
            action_type='USER_DELETE',
            description=f"Deleted user {email}",
            obj=user,
            request=request
        )

        messages.error(request, f"User {email} has been permanently deleted.")
        return super().delete(request, *args, **kwargs)


class ContactSupportView(View):
    """Handle contact form submissions via email."""

    def post(self, request):
        """Send contact email to support."""
        try:
            name = request.POST.get('name', '').strip()
            email_address = request.POST.get('email', '').strip()
            subject_line = request.POST.get('subject', '').strip()
            message_text = request.POST.get('message', '').strip()

            # Validation
            if not all([name, email_address, subject_line, message_text]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required'
                }, status=400)

            if len(message_text) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Message must be at least 10 characters'
                }, status=400)

            # Basic email format validation
            if '@' not in email_address:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide a valid email address'
                }, status=400)

            # Send email to support address
            support_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@dreambooksalon.com')

            # Email body to support
            email_message = f"""New Contact Form Submission

From: {name} ({email_address})
Subject: {subject_line}

Message:
{message_text}

---
This is an automated message from the Dreambook Salon contact form.
"""

            send_mail(
                f"Contact Form: {subject_line}",
                email_message,
                email_address,
                [support_email],
                fail_silently=False,
            )

            # Send confirmation email to user
            confirmation_message = f"""Dear {name},

Thank you for contacting Dreambook Salon. We have received your message and will respond within 24 hours.

Best regards,
Dreambook Salon Team
"""

            send_mail(
                "We received your message - Dreambook Salon",
                confirmation_message,
                support_email,
                [email_address],
                fail_silently=False,
            )

            return JsonResponse({
                'success': True,
                'message': 'Thank you for contacting us! We will respond within 24 hours.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to send message. Please try again later.'
            }, status=500)
