from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import CustomerRegistrationForm, EmailAuthenticationForm


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "featured_services": [
                    {
                        "name": "Precision Haircut",
                        "description": "Tailored cuts with relaxing wash and finish.",
                        "duration": "45 mins",
                        "price": "₱850",
                    },
                    {
                        "name": "Color & Gloss",
                        "description": "Vibrant color application with gloss sealing.",
                        "duration": "90 mins",
                        "price": "₱2,300",
                    },
                    {
                        "name": "Spa Manicure",
                        "description": "Nail shaping, cuticle care, and polish.",
                        "duration": "40 mins",
                        "price": "₱650",
                    },
                ],
                "inventory_highlights": [
                    {
                        "name": "Argan Oil Serum",
                        "status": "In stock",
                        "badge": "core",
                    },
                    {
                        "name": "Keratin Treatment Kit",
                        "status": "Low stock",
                        "badge": "warning",
                    },
                ],
                "booking_fields": [
                    {
                        "name": "service",
                        "label": "Choose service",
                        "placeholder": "Service name",
                    },
                    {
                        "name": "date",
                        "label": "Preferred date",
                        "type": "date",
                    },
                    {
                        "name": "time",
                        "label": "Preferred time",
                        "type": "time",
                    },
                ],
            }
        )
        return context


class EmailLoginView(LoginView):
    template_name = "pages/auth_login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "You're signed in. Welcome back!")
        return super().form_valid(form)


class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("core:login")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You've been signed out.")
        return super().dispatch(request, *args, **kwargs)


class CustomerRegistrationView(FormView):
    template_name = "pages/auth_register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Welcome aboard! You're now signed in.")
        return super().form_valid(form)
