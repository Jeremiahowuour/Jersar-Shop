# retailshop/app/forms.py

from django import forms
# Import the base form classes for Authentication
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
# Import your custom models
from .models import Category, Profile # Ensure you import the Profile model

# 1. User Registration Form (THE MISSING FORM)
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
        # Include first_name and last_name for better profile data
        fields = ['username', 'email', 'first_name', 'last_name'] 
        
# 3. Profile Update Form (FIXED: Changed from forms.Form to forms.ModelForm)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Assuming your Profile model has 'image', 'phone_number', and 'address' fields
        # You need to adjust 'fields' to match your actual Profile model fields.
        fields = ['image', 'phone_number', 'address'] 

# 4. Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Including 'description' as requested
        fields = ['name', 'slug', 'description']