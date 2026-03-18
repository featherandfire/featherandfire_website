from django import forms
from .models import SellerApplication


class SellerApplicationForm(forms.ModelForm):
    class Meta:
        model = SellerApplication
        fields = ['name', 'email', 'portfolio_url', 'message']
