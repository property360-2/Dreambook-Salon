from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .decorators import role_required


class AuthViewsTests(TestCase):
    def test_registration_creates_customer_and_logs_in(self):
        response = self.client.post(
            reverse("core:register"),
            data={
                "first_name": "Ami",
                "last_name": "Santos",
                "email": "ami@example.com",
                "password1": "ComplexPass!23",
                "password2": "ComplexPass!23",
            },
        )

        self.assertRedirects(response, reverse("core:home"))
        user = get_user_model().objects.get(email="ami@example.com")
        self.assertEqual(user.role, user.Roles.CUSTOMER)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_login_accepts_email_username_field(self):
        user = get_user_model().objects.create_user(
            email="staff@example.com",
            password="ComplexPass!23",
            role=get_user_model().Roles.STAFF,
        )

        response = self.client.post(
            reverse("core:login"),
            data={"username": "staff@example.com", "password": "ComplexPass!23"},
        )

        self.assertRedirects(response, reverse("core:home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)


class RoleRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_model = get_user_model()

    def _decorated_view(self):
        @role_required(self.user_model.Roles.ADMIN)
        def sample_view(request):
            return HttpResponse("ok")

        return sample_view

    def test_redirects_to_login_when_anonymous(self):
        view = self._decorated_view()
        request = self.factory.get("/secure/")
        request.user = AnonymousUser()

        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("core:login"), response.url)

    def test_raises_permission_denied_for_wrong_role(self):
        view = self._decorated_view()
        request = self.factory.get("/secure/")
        request.user = self.user_model.objects.create_user(
            email="customer@example.com",
            password="ComplexPass!23",
            role=self.user_model.Roles.CUSTOMER,
        )

        with self.assertRaises(PermissionDenied):
            view(request)

    def test_allows_matching_role(self):
        view = self._decorated_view()
        request = self.factory.get("/secure/")
        request.user = self.user_model.objects.create_user(
            email="admin@example.com",
            password="ComplexPass!23",
            role=self.user_model.Roles.ADMIN,
        )

        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
