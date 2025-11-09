from django import forms
from django.forms import inlineformset_factory
from .models import Service, ServiceItem
from inventory.models import Item


class ServiceForm(forms.ModelForm):
    """Form for creating and editing services."""

    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration_minutes', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., Hair Rebond'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Detailed description of the service...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'placeholder': 'Duration in minutes'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-dark-elevated border-dark-border rounded focus:ring-primary-500'
            }),
        }
        labels = {
            'name': 'Service Name',
            'description': 'Description',
            'price': 'Price (₱)',
            'duration_minutes': 'Duration (minutes)',
            'is_active': 'Active (available for booking)',
        }


class ServiceItemForm(forms.ModelForm):
    """Form for adding inventory items to a service."""

    class Meta:
        model = ServiceItem
        fields = ['item', 'qty_per_service']
        widgets = {
            'item': forms.Select(attrs={'class': 'input'}),
            'qty_per_service': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Quantity'
            }),
        }
        labels = {
            'item': 'Inventory Item',
            'qty_per_service': 'Quantity Used Per Service',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active inventory items
        self.fields['item'].queryset = Item.objects.filter(is_active=True).order_by('name')


# Formset for managing service items (inventory associations)
ServiceItemFormSet = inlineformset_factory(
    Service,
    ServiceItem,
    form=ServiceItemForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)
