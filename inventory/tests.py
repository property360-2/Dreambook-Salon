from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Item


class ItemModelTests(TestCase):
    def test_item_creation(self):
        item = Item.objects.create(
            name="Shampoo",
            description="Hair shampoo",
            unit="ml",
            stock=Decimal("100.00"),
            threshold=Decimal("20.00"),
        )
        self.assertEqual(item.name, "Shampoo")
        self.assertEqual(item.stock, Decimal("100.00"))
        self.assertEqual(item.threshold, Decimal("20.00"))
        self.assertTrue(item.is_active)

    def test_is_low_stock_property(self):
        item = Item.objects.create(
            name="Shampoo",
            stock=Decimal("15.00"),
            threshold=Decimal("20.00"),
            unit="ml",
        )
        self.assertTrue(item.is_low_stock)

        item.stock = Decimal("25.00")
        item.save()
        self.assertFalse(item.is_low_stock)

    def test_stock_status_property(self):
        # Out of stock
        item = Item.objects.create(
            name="Shampoo",
            stock=Decimal("0.00"),
            threshold=Decimal("20.00"),
            unit="ml",
        )
        self.assertEqual(item.stock_status, "Out of Stock")

        # Low stock
        item.stock = Decimal("15.00")
        item.save()
        self.assertEqual(item.stock_status, "Low Stock")

        # In stock
        item.stock = Decimal("50.00")
        item.save()
        self.assertEqual(item.stock_status, "In Stock")


class InventoryViewTests(TestCase):
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
        self.item = Item.objects.create(
            name="Shampoo",
            stock=Decimal("100.00"),
            threshold=Decimal("20.00"),
            unit="ml",
        )
        self.client.login(username="staff@example.com", password="testpass123")

    def test_inventory_list_requires_staff(self):
        response = self.client.get(reverse("inventory:list"))
        self.assertEqual(response.status_code, 200)

    def test_inventory_list_denied_for_customer(self):
        self.client.logout()
        self.client.login(username="customer@example.com", password="testpass123")

        response = self.client.get(reverse("inventory:list"))
        self.assertEqual(response.status_code, 403)

    def test_inventory_detail_view(self):
        response = self.client.get(reverse("inventory:detail", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["item"], self.item)

    def test_inventory_adjust_view(self):
        # Test that the endpoint is accessible and returns a redirect
        response = self.client.post(
            reverse("inventory:adjust", args=[self.item.id]),
            data={"adjustment": "10.00"},
        )
        # Should redirect after POST
        self.assertEqual(response.status_code, 302)


class LowStockAlertsTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff = self.user_model.objects.create_user(
            email="staff@example.com",
            password="testpass123",
            role=self.user_model.Roles.STAFF,
        )

        # Create items with different stock levels
        self.out_of_stock = Item.objects.create(
            name="Out of Stock Item",
            stock=Decimal("0.00"),
            threshold=Decimal("10.00"),
            unit="pcs",
        )
        self.low_stock = Item.objects.create(
            name="Low Stock Item",
            stock=Decimal("5.00"),
            threshold=Decimal("10.00"),
            unit="pcs",
        )
        self.in_stock = Item.objects.create(
            name="In Stock Item",
            stock=Decimal("50.00"),
            threshold=Decimal("10.00"),
            unit="pcs",
        )

        self.client.login(username="staff@example.com", password="testpass123")

    def test_alerts_view_shows_low_stock_items(self):
        response = self.client.get(reverse("inventory:alerts"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.out_of_stock, response.context["out_of_stock"])
        self.assertIn(self.low_stock, response.context["low_stock"])
