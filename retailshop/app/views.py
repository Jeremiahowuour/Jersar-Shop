from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
# 🆕 Added imports for form-based auth views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction 
# F is imported here:
from django.db.models import Q, Avg, F

# Import forms and models from your app
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm # 🆕 Added UserRegisterForm
from .models import Profile, Category, Product, Review, Cart, CartItem 

# Import M-Pesa client
from django_daraja.mpesa.core import MpesaClient

# 🎯 HOME VIEW
def home(request):
    """Renders the homepage, fetching all categories with related products."""
    all_categories = Category.objects.prefetch_related('products').all()
    context = {
        'categories': all_categories,
    }
    return render(request, 'app/home.html', context)

# ... (products, product_detail, add_to_cart, cart_view, update_cart views are correct) ...

# 🎯 PRODUCTS VIEW (Consolidated, database-driven)
def products(request):
    """Renders the product listing page, supporting filtering by category and search."""
    
    # 1. Fetch all categories (for sidebar/filter menu)
    categories = Category.objects.all()
    
    # 2. Start with all products
    all_products = Product.objects.all()
    title = "All Products"
    category_name = None
    
    # 3. Handle Filtering by Category
    category_name = request.GET.get('category')
    if category_name:
        all_products = all_products.filter(category__name=category_name)
        title = f"Products in {category_name}"
    
    # 4. Handle Search
    search_query = request.GET.get('q')
    if search_query:
        all_products = all_products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
        title = f"Search Results for '{search_query}'"

    # 5. Prepare the context dictionary
    context = {
        'title': title,
        'products': all_products,
        'categories': categories,
        'selected_category': category_name, 
    }
    
    return render(request, 'app/products.html', context)


# 🎯 PRODUCT DETAIL VIEW (Consolidated, database-driven with reviews)
def product_detail(request, pk):
    """Fetches a single product and related data from the database."""
    
    # Use the database model to fetch the product by its Primary Key (pk)
    product = get_object_or_404(Product, pk=pk)
    
    # Fetch Reviews/Ratings
    reviews = product.reviews.all().order_by('-created_at') 
    
    # Calculate average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Fetch Related Products
    related_products = Product.objects.filter(
        category=product.category 
    ).exclude(pk=pk).order_by('?')[:3]
    
    context = {
        "product": product,
        "reviews": reviews,
        "average_rating": average_rating,
        "related_products": related_products,
    }
    
    return render(request, "app/product_detail.html", context)


#  ADD TO CART VIEW (Consolidated, database-driven)
 

@login_required(login_url='login')
def add_to_cart(request, product_id):
   
    product = get_object_or_404(Product, pk=product_id)
    
    # 1. Get the user's Cart object (It is now guaranteed to exist)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get quantity from the form, defaulting to 1 and ensuring it's an integer > 0
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                quantity = 1
        except ValueError:
            quantity = 1

        # 2. Try to retrieve the existing CartItem or create a new one
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            # If it's a new item, 'defaults' will set the initial quantity
            defaults={'quantity': quantity} 
        )

        if created:
            # 3. If a new item was created
            messages.success(request, f"Added {quantity} x '{product.name}' to your cart.")
        else:
            # 4. If the item already exists, update its quantity atomically
            cart_item.quantity = F('quantity') + quantity
            cart_item.save()
            
            # Since F() updates are applied at the database level, 
            # we need to reload the object to see the updated value for the message.
            cart_item.refresh_from_db()

            messages.success(
                request, 
                f"Added {quantity} more to the cart. Total: {cart_item.quantity} x {product.name}."
            )
    
    # If the request method is GET, it should generally redirect to prevent double-submits
    return redirect('cart_view')

#  CART VIEW
@login_required(login_url='login')
def cart_view(request):
    """Renders the shopping cart page with items and totals."""
    try:
        # Fetch the user's cart (or it will throw an exception if the Cart object doesn't exist yet)
        cart = Cart.objects.get(user=request.user)
        
        # Prefetch the product details to avoid N+1 queries
        cart_items = cart.items.select_related('product') 
        
        # Calculate totals
        cart_total = sum(item.subtotal() for item in cart_items)
        
        context = {
            "cart_items": cart_items,
            "cart_total": cart_total,
        }
    except Cart.DoesNotExist:
        # Handle the case where the user hasn't added anything yet (no cart object)
        context = {
            "cart_items": [],
            "cart_total": 0.00,
        }
        
    return render(request, "app/cart.html", context)


# UPDATE CART VIEW
@login_required(login_url='login')
def update_cart(request, product_id):
    """
    Handles POST request to update the quantity of a CartItem.
    The product_id is needed to find the specific CartItem for the current user.
    """
    if request.method == 'POST':
        # 1. Get the new quantity from the form
        new_quantity = request.POST.get('quantity')

        # 2. Find the CartItem for the current user and product
        try:
            cart_item = CartItem.objects.get(
                cart__user=request.user, 
                product__pk=product_id
            )
            
            if new_quantity and int(new_quantity) > 0:
                cart_item.quantity = int(new_quantity)
                cart_item.save()
                messages.success(request, f"Quantity for {cart_item.product.name} updated.")
            elif int(new_quantity) == 0:
                cart_item.delete()
                messages.warning(request, f"{cart_item.product.name} removed from cart.")
                
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in your cart.")
            
    # Always redirect back to the cart page
    return redirect('cart_view')


# --- PRODUCT CATEGORY VIEWS ---
def categories(request):
    """Renders a list of all product categories."""
    
    # Fetch all Category objects from the database
    all_categories = Category.objects.all()
    
    context = {
        'categories': all_categories,
        'title': 'All Product Categories'
    }
    
    return render(request, 'app/categories.html', context)


@login_required(login_url='login')
def update_category(request, category_slug):
    """
    Handles updating an existing Category object.
    Requires a category_slug to fetch the object.
    """
    # 1. Fetch the existing category instance using the slug
    category = get_object_or_404(Category, slug=category_slug)

    if request.method == 'POST':
        # 2. Bind the POST data and the existing instance to the form
        form = CategoryForm(request.POST, instance=category)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully.")
            # Redirect to the category list or the updated category's page
            return redirect('categories')  # Assuming you have a 'categories' list view

    else:
        # 3. For GET request, pre-populate the form with existing instance data
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f"Update Category: {category.name}"
    }
    return render(request, 'app/update_category.html', context)


# --- USER AUTHENTICATION VIEWS ---

def register_user(request):
    """Handles user registration using the UserRegisterForm."""
    if request.method == 'POST':
        # 🟢 CRITICAL FIX: Include request.FILES for file uploads (like profile_image)
        form = UserRegisterForm(request.POST, request.FILES) 
        
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login') 
            
        # 🟢 If validation fails, the form object (with errors) is passed to the context.
        # This is where the errors are finally visible in your custom template.
            
    else:
        form = UserRegisterForm()
        
    context = {'form': form, 'title': 'Register'}
    # Standard render call is correct.
    return render(request, 'app/register.html', context)


# --- USER PROFILE VIEWS ---    

#  PROFILE VIEW (Basic implementation)
@login_required(login_url='login')
def profile_view(request):
    """Renders the user profile page."""
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'title': 'User Profile'
    }
    return render(request, 'app/profile.html', context)


# 🎯 PROFILE EDIT VIEW (Basic implementation)
@login_required(login_url='login')
@transaction.atomic # Ensures both forms are saved or neither is
def profile_edit_view(request):
    """Handles updating User and Profile data."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
            
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Edit Profile'
    }
    return render(request, 'app/profile_edit.html', context)

# app/views.py

import json # Added import for handling M-Pesa JSON callback data
# ... (all your existing imports) ...

# -------------------------------------------------------------
# --- MPESA INTEGRATION VIEWS (UPDATED) -----------------------
# -------------------------------------------------------------

# Initialize MpesaClient (Do this outside the function for performance)
cl = MpesaClient()

# Define the callback URL (MUST match the path defined in your app/urls.py)
# e.g., If your callback path is 'mpesa/callback/', the URL is the full host address:
# NOTE: Use ngrok or a public URL for a real M-Pesa setup!
CALLBACK_URL = 'https://your_public_url.com/app/mpesa/callback/'
# For local testing, you might just use a placeholder until you integrate ngrok:
# CALLBACK_URL = 'https://example.com/app/mpesa/callback/' # <<< Change this when testing live

@login_required(login_url='login')
def initiate_mpesa(request, product_id):
    """Initiates the M-Pesa STK push based on user input."""
    if request.method == 'POST':
        # 1. Get the data
        phone_number = request.POST.get('phone_number')
        quantity = request.POST.get('quantity', 1)
        
        # Input validation for quantity and phone number (basic)
        try:
            quantity = int(quantity)
            if quantity <= 0:
                quantity = 1
        except ValueError:
            quantity = 1
            
        if not phone_number or len(phone_number) < 12: # Expecting 2547...
            messages.error(request, "Invalid phone number format. Use 2547XXXXXXXX.")
            return redirect('products')

        # 2. Get Product and calculate amount
        product = get_object_or_404(Product, id=product_id)
        # Use a minimum amount (1.0) for testing, as M-Pesa fails on 0
        amount = max(1.0, product.price * quantity)
        
        # 3. Call M-Pesa STK Push API
        try:
            # The 'amount' should be in KES, but must be an integer for Daraja API
            amount_int = int(amount)
            account_reference = f"RTS{product_id}-{request.user.id}" # Unique identifier
            transaction_desc = f"Payment for {product.name}"
            
            # 🛑 CRITICAL: Ensure you use the globally defined CALLBACK_URL
            response = cl.stk_push(
                phone_number, 
                amount_int, 
                CALLBACK_URL, 
                account_reference, 
                transaction_desc
            )
            
            # 4. Handle API Response
            # The response will contain a CheckoutRequestID and MerchantRequestID
            # You should save this response data to your database (Order/Transaction table)
            
            messages.success(request, f"M-Pesa STK Push initiated for Ksh {amount_int} to {phone_number}. Please enter your M-Pesa PIN.")
            return redirect('products') 
            
        except Exception as e:
            messages.error(request, f"M-Pesa initiation failed. Please try again. Error: {e}")
            return redirect('products')

    # Should only be reachable via POST from the form
    return redirect('products')
@login_required(login_url='login')
def checkout_view(request):
    """
    Renders the final checkout page, confirming cart contents and collecting
    final order details (like address and selected payment method).
    """
    # Fetch the user's cart and calculate total
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        cart_total = sum(item.subtotal() for item in cart_items)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('products') # Redirect if nothing to checkout

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        # You would add forms for shipping/address here later
    }
    return render(request, 'app/checkout.html', context)

def mpesa_callback(request):
    """
    M-Pesa confirmation callback view.
    Receives JSON data from the M-Pesa servers.
    """
    # This view must respond with HTTP 200 (OK) to M-Pesa
    if request.method == 'POST':
        try:
            # Decode the JSON payload sent by Safaricom
            data = json.loads(request.body.decode('utf-8'))
            
            # 🛑 Implement your logging and database update logic here
            # 1. Log the incoming data for auditing.
            # 2. Extract transaction details (ResultCode, MerchantRequestID, MpesaReceiptNumber, Amount).
            # 3. Find the pending Order/Transaction in your database using MerchantRequestID or AccountReference.
            # 4. If ResultCode == 0, mark the order as paid, update stock, and notify the user (via email/websocket).

            # Mandatory response for M-Pesa API
            return HttpResponse("OK", status=200) 
            
        except json.JSONDecodeError:
            # Handle invalid JSON payload
            return HttpResponse(status=400) 
        except Exception as e:
            # Handle any internal processing errors
            # You should log this error: f"Error processing M-Pesa callback: {e}"
            return HttpResponse(status=500)
            
    # Block all GET requests to this sensitive URL
    return HttpResponse(status=405) # Method Not Allowed

@login_required(login_url='login')
def generic_checkout_view(request):
    messages.info(request, "This is the generic checkout page. Logic needs implementation.")
    # Implement cart checkout logic here
    return render(request, 'app/checkout.html', {})

# 🎯 CASH CHECKOUT VIEW (Placeholder - kept for completeness)
@login_required(login_url='login')
def cash_checkout_view(request, product_id):
    """Handles the Cash payment/order confirmation."""
    # Note: Use the quantity from the POST request if needed, but for 'Buy Now' quantity is usually 1.
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        # 1. Get quantity (from the hidden form field)
        quantity = request.POST.get('quantity', 1)
        
        # 2. Implement Order Creation/Storage with Payment Type='Cash' here
        # Example: Order.objects.create(user=request.user, product=product, quantity=quantity, payment_type='Cash')
        
        messages.success(request, f"Order for {quantity} x {product.name} confirmed. You will pay Cash on Delivery/Collection.")
        return redirect('home') # Redirect to a success page

    return redirect('products') # Redirect if accessed via GET