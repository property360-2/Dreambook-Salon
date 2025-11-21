from django import forms
from .models import GCashQRCode


class GCashQRCodeForm(forms.ModelForm):
    """Form for uploading and managing GCash QR code."""

    class Meta:
        model = GCashQRCode
        fields = ['description', 'qr_image', 'is_active']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., GCash Receive Payment',
            }),
            'qr_image': forms.FileInput(attrs={
                'class': 'input',
                'accept': 'image/*',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-light-elevated border-light-border rounded focus:ring-primary-500'
            }),
        }
        labels = {
            'description': 'Description',
            'qr_image': 'QR Code Image',
            'is_active': 'Make Active',
        }
