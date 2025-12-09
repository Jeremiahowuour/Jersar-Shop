from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from app.views import CustomLoginView

urlpatterns = [
    # 🛑 REMOVED THE PROBLEM LINE: path('mpesa/', views.mpesa_payment, name='mpesa_payment'),
    
    # ------------------------------------------------------------------
    # 🟢 M-PESA & CHECKOUT VIEWS (Combined the new paths here)
    # ------------------------------------------------------------------
    # M-Pesa Initiation (Used by the 'Buy Now' form)
    path('mpesa/initiate/<int:product_id>/', views.initiate_mpesa, name='initiate_mpesa'),
    
    # M-Pesa Callback (Used by the Safaricom API)
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # Cash Checkout (Used by the cash form)
    path('cash/checkout/<int:product_id>/', views.cash_checkout_view, name='cash_checkout'),
    
    # ------------------------------------------------------------------
    # Public Views
    # ------------------------------------------------------------------
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    
    # Detail/Cart Actions (Needs the ID)
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), 
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    
    # Authentication Views
    path("login/", auth_views.LoginView.as_view(template_name='app/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='/app/login/'), name="logout"),
    path("register/", views.register_user, name="register"), 
    
    # User/Cart Views
    path('cart/', views.cart_view, name='cart_view'),
    
    # User profile Views
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/process/', views.process_order, name='process_order'),
    # CATEGORY Views
    path('categories/', views.categories, name='categories'), 
    path('categories/update/<slug:category_slug>/', views.update_category, name='update_category'),
    path('admin/sales/', views.sales_dashboard, name='sales_dashboard'),
    path('login/', CustomLoginView.as_view(template_name='app/login.html'), name='login'),
]

# Static/Media Files Configuration (Keep this at the end)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)