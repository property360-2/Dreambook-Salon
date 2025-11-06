from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment, AppointmentSettings, BlockedRange
from services.models import Service
from inventory.models import Item
from services.models import ServiceItem


class AppointmentModelTests(TestCase):
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

    def test_appointment_end_time_auto_calculated(self):
        start = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=start,
        )
        expected_end = start + timedelta(minutes=60)
        self.assertEqual(appointment.end_at, expected_end)

    def test_is_upcoming_property(self):
        future_appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(future_appointment.is_upcoming)

    def test_is_past_property(self):
        past_appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(past_appointment.is_past)

    def test_default_status_is_pending(self):
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
        )
        self.assertEqual(appointment.status, "pending")

    def test_default_payment_state_is_unpaid(self):
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
        )
        self.assertEqual(appointment.payment_state, "unpaid")


class AppointmentSettingsTests(TestCase):
    def test_get_settings_returns_singleton(self):
        settings1 = AppointmentSettings.get_settings()
        settings2 = AppointmentSettings.get_settings()
        self.assertEqual(settings1.id, settings2.id)

    def test_default_max_concurrent_is_three(self):
        settings = AppointmentSettings.get_settings()
        self.assertEqual(settings.max_concurrent, 3)

    def test_default_booking_window_is_thirty_days(self):
        settings = AppointmentSettings.get_settings()
        self.assertEqual(settings.booking_window_days, 30)


class BlockedRangeTests(TestCase):
    def test_overlaps_method_detects_overlap(self):
        blocked = BlockedRange.objects.create(
            start_at=timezone.now(),
            end_at=timezone.now() + timedelta(hours=2),
            reason="Lunch break",
        )

        # Overlapping range
        overlap_start = timezone.now() + timedelta(hours=1)
        overlap_end = timezone.now() + timedelta(hours=3)
        self.assertTrue(blocked.overlaps(overlap_start, overlap_end))

    def test_overlaps_method_no_overlap(self):
        blocked = BlockedRange.objects.create(
            start_at=timezone.now(),
            end_at=timezone.now() + timedelta(hours=2),
            reason="Lunch break",
        )

        # Non-overlapping range
        no_overlap_start = timezone.now() + timedelta(hours=3)
        no_overlap_end = timezone.now() + timedelta(hours=4)
        self.assertFalse(blocked.overlaps(no_overlap_start, no_overlap_end))


class AppointmentCompleteViewTests(TestCase):
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
        self.item = Item.objects.create(
            name="Shampoo",
            stock=Decimal("100.00"),
            unit="ml",
        )
        ServiceItem.objects.create(
            service=self.service,
            item=self.item,
            qty_per_service=Decimal("10.00"),
        )
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            start_at=timezone.now() + timedelta(days=1),
            status="in_progress",
        )
        self.client.login(username="staff@example.com", password="testpass123")

    def test_complete_appointment_deducts_inventory(self):
        initial_stock = self.item.stock
        response = self.client.post(
            reverse("appointments:complete", args=[self.appointment.id])
        )

        self.appointment.refresh_from_db()
        self.item.refresh_from_db()

        self.assertEqual(self.appointment.status, "completed")
        self.assertEqual(self.item.stock, initial_stock - Decimal("10.00"))

    def test_staff_required_for_complete(self):
        self.client.logout()
        self.client.login(username="customer@example.com", password="testpass123")

        response = self.client.post(
            reverse("appointments:complete", args=[self.appointment.id])
        )
        self.assertEqual(response.status_code, 403)
