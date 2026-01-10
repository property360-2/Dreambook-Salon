from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    """Form for creating and editing inventory items."""

    class Meta:
        model = Item
        fields = ['name', 'category', 'description', 'unit', 'stock', 'threshold', 'expiry_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., Shampoo',
            }),
            'category': forms.Select(attrs={
                'class': 'input',
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'Item description...'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., ml, pcs, kg'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'threshold': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0',
                'placeholder': '10.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-dark-elevated border-dark-border rounded focus:ring-primary-500'
            }),
        }
        labels = {
            'name': 'Item Name',
            'category': 'Category',
            'description': 'Description',
            'unit': 'Unit of Measurement',
            'stock': 'Current Stock',
            'threshold': 'Low Stock Threshold',
            'expiry_date': 'Expiration Date',
            'is_active': 'Active (tracked in inventory)',
        }


class RestockForm(forms.Form):
    """Form for restocking inventory items."""

    quantity = forms.DecimalField(
        min_value=0.01,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Quantity to add',
            'autofocus': True,
        }),
        label='Restock Quantity',
        help_text='Enter the quantity to add to current stock'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input',
            'rows': 3,
            'placeholder': 'Optional notes about this restock...'
        }),
        label='Notes',
        help_text='Optional notes or reason for restocking'
    )


class AdjustStockForm(forms.Form):
    """Form for adjusting stock (can be positive or negative)."""

    adjustment = forms.DecimalField(
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'step': '0.01',
            'placeholder': '±quantity (e.g., +10 or -5)',
            'autofocus': True,
        }),
        label='Stock Adjustment',
        help_text='Positive to add, negative to subtract. Example: +10 or -5'
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input',
            'rows': 2,
            'placeholder': 'Reason for adjustment...'
        }),
        label='Reason',
        help_text='Optional reason for this adjustment'
    )

    def clean_adjustment(self):
        adjustment = self.cleaned_data.get('adjustment')
        if adjustment == 0:
            raise forms.ValidationError('Adjustment cannot be zero.')
        return adjustment
