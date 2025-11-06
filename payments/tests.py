from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment
from payments.models import Payment
from services.models import Service


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
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
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            appointment=self.appointment,
            method="GCASH",
            amount=Decimal("500.00"),
            txn_id="TXN-TEST-001",
        )
        self.assertEqual(payment.appointment, self.appointment)
        self.assertEqual(payment.method, "GCASH")
        self.assertEqual(payment.amount, Decimal("500.00"))

    def test_default_status_is_pending(self):
        payment = Payment.objects.create(
            appointment=self.appointment,
            method="GCASH",
            amount=Decimal("500.00"),
            txn_id="TXN-TEST-001",
        )
        self.assertEqual(payment.status, "pending")

    def test_is_successful_property(self):
        payment = Payment.objects.create(
            appointment=self.appointment,
            method="GCASH",
            amount=Decimal("500.00"),
            txn_id="TXN-TEST-001",
            status="paid",
        )
        self.assertTrue(payment.is_successful)

        payment.status = "FAILED"
        payment.save()
        self.assertFalse(payment.is_successful)

    def test_txn_id_generated(self):
        payment = Payment.objects.create(
            appointment=self.appointment,
            method="GCASH",
            amount=Decimal("500.00"),
            txn_id="TXN-TEST-001",
        )
        self.assertIsNotNone(payment.txn_id)
        self.assertTrue(payment.txn_id.startswith("TXN-"))


class PaymentViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
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
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
        )
        self.client.login(username="customer@example.com", password="testpass123")

    def test_payment_initiate_view_accessible(self):
        response = self.client.get(
            reverse("payments:initiate", args=[self.appointment.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_payment_list_view_accessible(self):
        response = self.client.get(reverse("payments:list"))
        self.assertEqual(response.status_code, 200)


class PaymentStatsViewTests(TestCase):
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

    def test_stats_view_requires_staff(self):
        response = self.client.get(reverse("payments:stats"))
        self.assertEqual(response.status_code, 200)

    def test_stats_view_denied_for_customer(self):
        self.client.logout()
        self.client.login(username="customer@example.com", password="testpass123")

        response = self.client.get(reverse("payments:stats"))
        self.assertEqual(response.status_code, 403)
