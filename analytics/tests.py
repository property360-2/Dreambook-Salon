from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment
from payments.models import Payment
from services.models import Service


class AnalyticsDashboardViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff = self.user_model.objects.create_user(
            email="staff@example.com",
            password="testpass123",
            role=self.user_model.Roles.STAFF,
        )
        self.customer = self.user_model.objects.create_user(
            email="customer@example.com",
            password="testpass123",
            role=self.user_model.Roles.CUSTOMER,
        )
        self.client.login(username="staff@example.com", password="testpass123")

    def test_dashboard_requires_staff(self):
        response = self.client.get(reverse("analytics:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_denied_for_customer(self):
        self.client.logout()
        self.client.login(username="customer@example.com", password="testpass123")

        response = self.client.get(reverse("analytics:dashboard"))
        self.assertEqual(response.status_code, 403)


class RevenueChartViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff = self.user_model.objects.create_user(
            email="staff@example.com",
            password="testpass123",
            role=self.user_model.Roles.STAFF,
        )
        self.customer = self.user_model.objects.create_user(
            email="customer@example.com",
            password="testpass123",
            role=self.user_model.Roles.CUSTOMER,
        )
        self.service = Service.objects.create(
            name="Haircut",
            price=Decimal("500.00"),
            duration_minutes=60,
        )

        # Create appointments and payments
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
        )
        self.payment = Payment.objects.create(
            appointment=self.appointment,
            method="GCASH",
            amount=Decimal("500.00"),
            status="PAID",
        )

        self.client.login(username="staff@example.com", password="testpass123")

    def test_revenue_view_accessible(self):
        response = self.client.get(reverse("analytics:revenue"))
        self.assertEqual(response.status_code, 200)


class ServiceAnalyticsViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff = self.user_model.objects.create_user(
            email="staff@example.com",
            password="testpass123",
            role=self.user_model.Roles.STAFF,
        )
        self.client.login(username="staff@example.com", password="testpass123")

    def test_service_analytics_accessible(self):
        response = self.client.get(reverse("analytics:services"))
        self.assertEqual(response.status_code, 200)


class InventoryAnalyticsViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff = self.user_model.objects.create_user(
            email="staff@example.com",
            password="testpass123",
            role=self.user_model.Roles.STAFF,
        )
        self.client.login(username="staff@example.com", password="testpass123")

    def test_inventory_analytics_accessible(self):
        response = self.client.get(reverse("analytics:inventory"))
        self.assertEqual(response.status_code, 200)
