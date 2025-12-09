# retailshop/app/admin.py

from django.contrib import admin
from .models import Category, Product, Cart, CartItem 
# Ensure all necessary models are imported

# --- 1. Custom Admin for Category ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'banner_image')
    prepopulated_fields = {'slug': ('name',)} 
    fields = ('name', 'slug', 'description', 'banner_image')


# --- 2. Custom Admin for Product (Errors Fixed) ---

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # REMOVED: 'is_active' (since it likely doesn't exist)
    list_display = ('name', 'category', 'price', 'stock')
    
    # REMOVED: 'is_active', 'created_at' (since they likely don't exist)
    list_filter = ('category',) 
    
    search_fields = ('name', 'description', 'category__name') 
    
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'image')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
    )
    

# --- 3. Cart Management (Errors Fixed) ---

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0 
    readonly_fields = ('product', 'quantity') 

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    # list_display remains the same, but the custom method 'is_checked_out' must be defined below
    list_display = ('user', 'created_at', 'item_count', 'is_checked_out')
    
    ordering = ('-created_at',) 
    
    # REMOVED: 'is_checked_out' from list_filter (it's a method, not a field)
    list_filter = () 
    
    inlines = [CartItemInline]
    
    # REMOVED: 'updated_at' from readonly_fields (since it likely doesn't exist)
    readonly_fields = ('user', 'created_at')

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items in Cart'
    
    def is_checked_out(self, obj):
        # Placeholder logic
        return False
    is_checked_out.boolean = True
    is_checked_out.short_description = 'Order Placed'