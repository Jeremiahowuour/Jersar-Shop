from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
# F is imported here, but not used in models.py itself (it's for views)
# It's better practice to import it in views.py, but keeping it here is harmless.
from django.db.models import F 


# --- CORE E-COMMERCE MODELS ---

# 1. Category Model (Consolidated and defined only once)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True) 

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Requires 'from django.urls import reverse' at the top
        return reverse('category_products', args=[self.slug])

# 2. Product Model
class Product(models.Model):
    category = models.ForeignKey(
        'app.Category', 
        related_name='products', 
        on_delete=models.CASCADE
    )
    
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True) 

    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

# 3. Review Model
class Review(models.Model):
    product = models.ForeignKey(
        'Product', # Use string reference for safety if models are out of order
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    RATING_CHOICES = [
        (1, '⭐'), (2, '⭐⭐'), (3, '⭐⭐⭐'), (4, '⭐⭐⭐⭐'), (5, '⭐⭐⭐⭐⭐'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    
    text = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('product', 'user') 

    def __str__(self):
        return f"{self.rating} star review for {self.product.name}"

# --- USER PROFILE MODELS ---

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 🟢 Add these fields:
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone_number = models.CharField(max_length=15, blank=True, null=True) 
    address = models.TextField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} Profile"

# --- CART MODELS ---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items') 
    product = models.ForeignKey('Product', on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product') 
        
    def subtotal(self):
        # NOTE: Be careful with self.product.price, it might require extra checks
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# --- SIGNALS ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a Profile object automatically when a User object is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the Profile object whenever the User object is saved."""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # If the profile doesn't exist for some reason, create it
        Profile.objects.create(user=instance)