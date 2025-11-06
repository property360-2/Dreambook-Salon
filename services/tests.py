from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Item
from services.models import Service, ServiceItem


class ServiceModelTests(TestCase):
    def test_service_creation(self):
        service = Service.objects.create(
            name="Haircut",
            description="Basic haircut service",
            price=Decimal("500.00"),
            duration_minutes=60,
        )
        self.assertEqual(service.name, "Haircut")
        self.assertEqual(service.price, Decimal("500.00"))
        self.assertEqual(service.duration_minutes, 60)
        self.assertTrue(service.is_active)

    def test_service_default_is_active(self):
        service = Service.objects.create(
            name="Haircut",
            price=Decimal("500.00"),
            duration_minutes=60,
        )
        self.assertTrue(service.is_active)


class ServiceItemTests(TestCase):
    def setUp(self):
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

    def test_service_item_creation(self):
        service_item = ServiceItem.objects.create(
            service=self.service,
            item=self.item,
            qty_per_service=Decimal("10.00"),
        )
        self.assertEqual(service_item.service, self.service)
        self.assertEqual(service_item.item, self.item)
        self.assertEqual(service_item.qty_per_service, Decimal("10.00"))

    def test_service_item_unique_together(self):
        ServiceItem.objects.create(
            service=self.service,
            item=self.item,
            qty_per_service=Decimal("10.00"),
        )

        # Should not be able to create duplicate
        with self.assertRaises(Exception):
            ServiceItem.objects.create(
                service=self.service,
                item=self.item,
                qty_per_service=Decimal("20.00"),
            )


class ServiceViewTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name="Haircut",
            price=Decimal("500.00"),
            duration_minutes=60,
            is_active=True,
        )

    def test_service_list_view(self):
        response = self.client.get(reverse("services:list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.service, response.context["services"])

    def test_service_detail_view(self):
        response = self.client.get(reverse("services:detail", args=[self.service.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["service"], self.service)

    def test_inactive_service_not_in_list(self):
        self.service.is_active = False
        self.service.save()

        response = self.client.get(reverse("services:list"))
        self.assertNotIn(self.service, response.context["services"])
