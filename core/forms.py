from django import forms
from django.contrib.auth.models import User

from .models import CustomerProfile, SellerProfile, Product


class CustomerRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') and cleaned.get('confirm_password'):
            if cleaned['password'] != cleaned['confirm_password']:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned


class SellerRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    shop_name = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') and cleaned.get('confirm_password'):
            if cleaned['password'] != cleaned['confirm_password']:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'image',
            'original_price', 'discounted_price',
            'quantity_available', 'expiry_date', 'pickup_window',
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        original = cleaned.get('original_price')
        discounted = cleaned.get('discounted_price')
        if original is not None and discounted is not None:
            if discounted <= 0:
                raise forms.ValidationError("Discounted price must be greater than 0.")
            if discounted >= original:
                raise forms.ValidationError(
                    "Discounted price should be lower than the original price."
                )
        return cleaned


class OrderForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    disclaimer_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must read and accept the expiry disclaimer to place this order.'}
    )
