from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class StyledFormMixin:
    """Apply Dreambook atom styles to Django form widgets."""

    input_class = "atom-input__control"

    def _apply_widget_styles(self):
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (
                f"{existing_classes} {self.input_class}".strip()
            )
            field.widget.attrs.setdefault("placeholder", field.label)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_widget_styles()


class EmailAuthenticationForm(StyledFormMixin, AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput())


class CustomerRegistrationForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="First name")
    last_name = forms.CharField(max_length=150, required=True, label="Last name")
    email = forms.EmailField(label="Work email")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.CUSTOMER
        if commit:
            user.save()
        return user


class UserManagementForm(StyledFormMixin, forms.ModelForm):
    """Form for creating and editing users in admin/staff interface."""

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        help_text="Leave blank to keep the current password"
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role", "is_active")

    def clean_email(self):
        """Validate email uniqueness (except for the current user)."""
        email = self.cleaned_data.get("email")
        if email:
            # Exclude current user if editing
            qs = User.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")

        # Only set password if provided
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user
