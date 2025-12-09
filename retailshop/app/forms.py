# retailshop/app/forms.py

from django import forms
# Import the base form classes for Authentication
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
# Import your custom models
from .models import Category, Profile # Ensure you import the Profile model

# 1. User Registration Form
class UserRegisterForm(UserCreationForm):
    # Optional: Adds the email field to the registration form and makes it required
    email = forms.EmailField(required=True) 
    
    class Meta:
        model = User
        fields = ['username', 'email']

# 2. User Update Form
class UserUpdateForm(forms.ModelForm):
    # Optional: Adds the email field and makes it required
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name'] 
        
# 3. Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Assuming your Profile model has 'image', 'phone_number', and 'address' fields
        fields = ['image', 'phone_number', 'address'] 

# 4. Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Including 'description' as requested
        fields = ['name', 'slug', 'description']

# 5. 🟢 CRITICAL: CHECKOUT FORM (The missing piece)
class CheckoutForm(forms.Form):
    """
    Form to collect the user's shipping/billing address details
    at the final checkout step.
    """
    first_name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        label="Phone Number", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 07XXXXXXXX'})
    )
    address_line_1 = forms.CharField(
        max_length=255, 
        required=True, 
        label="Delivery Address", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address, building name, or landmark'})
    )
    city = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City or Town'})
    )