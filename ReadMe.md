# 🛍️ RetailShop: A Django E-Commerce Starter Project

A foundational Django application designed to simulate a basic retail environment, featuring a **database-driven product catalog**, **user cart/checkout logic**, and **M-Pesa STK Push payment integration** using `django-daraja`.

---

## 🚀 1. Setup and Installation

Follow these steps to get the project running locally.

### 1.1. Prerequisites

You must have **Python 3.8+** installed on your system.

### 1.2. Virtual Environment

It is highly recommended to use a virtual environment for dependency management.

```bash
# 1. Create the virtual environment
python -m venv env

# 2. Activate the environment
# Windows (Command Prompt):
# env\Scripts\activate
# Windows (PowerShell) or Linux/macOS:
source env/bin/activate
```

### 1.3. Dependencies

Install Django, image-processing library (Pillow), and the M-Pesa client (`django-daraja`).

```bash
pip install Django Pillow django-daraja
```

### 1.4. Database Migration

The project now uses database models for Products, Categories, and Cart logic.

```bash
# 1. Create migration files for the 'app'
python manage.py makemigrations app

# 2. Apply all migrations (creates User, Profile, Product, Category, Cart tables, etc.)
python manage.py migrate
```

***

## ⚙️ 2. Configuration

### 2.1. M-Pesa Integration (Crucial)

To use the M-Pesa STK Push feature, you **must** configure your Daraja API credentials in `retailshop/settings.py` and define a public callback URL.

* **`settings.py`**: Add the required settings for `django-daraja` (Consumer Key, Secret, Business Shortcode, Passkey, etc.).
* **Callback URL**: The M-Pesa callback URL needs to be publicly accessible (e.g., using **Ngrok** in development) for Safaricom to send transaction results.
    * The callback view is mapped to: `/app/mpesa/callback/`

### 2.2. Media Files (User Uploads)

To ensure profile images and product images are served correctly in development, your `retailshop/urls.py` must include the static file serving logic:

```python
# retailshop/urls.py
# ...
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 2.3. Default Profile Image

The profile image template logic relies on a fallback. Ensure you create the necessary default image file:

* Create a folder structure: `app/static/images/`
* Place a placeholder image inside it named: **`default_profile.png`**

***

## 🔑 3. Key Features

### User Authentication & Profiles

The standard Django User model is extended with a custom `Profile` model.

* **Registration & Login:** Uses standard Django form-based authentication (`UserRegisterForm`).
* **Profile Integration:** The `Profile` model uses a **signal** to ensure a corresponding profile is automatically created for every new user.
    * *Access in templates:* `user.profile.image.url`

### E-Commerce Core Logic (Database-Driven)

The project now uses Django models (`Product`, `Category`, `Cart`, `CartItem`) for all product, catalog, and shopping cart operations.

* **Product Views:** Supports listing, searching, and filtering products by category.
* **Cart Management:**
    * **Add/Update Cart (`/app/add/<id>/`, `/app/update/<id>/`):** Handles adding new items and updating quantities (or removing items by setting quantity to 0).
    * **Cart View (`/app/cart/`):** Displays items and calculates totals.

### 💳 M-Pesa Payment Integration

The project includes functional views to initiate and confirm M-Pesa payments.

* **STK Push Initiation (`/app/mpesa/initiate/<id>/`):** Uses `MpesaClient.stk_push()` to send the payment request to the user's phone.
* **Confirmation Callback (`/app/mpesa/callback/`):** This view receives the transaction success/failure data from Safaricom. **Crucially, you must implement logic here to update the Order/Transaction status in your database.**
* **Cash Checkout (`/app/cash/checkout/<id>/`):** Placeholder for cash-on-delivery orders.

***

## 4. Running the Project

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

***

## 📝 5. Next Steps / Future Development

1.  **Order Model:** Create an **`Order`** model to store finalized purchases and track M-Pesa `TransactionId` and status.
2.  **M-Pesa Callback Persistence:** Implement logic in `mpesa_callback` to save the received JSON data to the new `Order` model and update inventory/stock.
3.  **Address/Shipping Forms:** Implement a form on the `/checkout/` page to collect the user's shipping address before confirming payment.
4.  **Admin Customization:** Register all new models in `app/admin.py` for easier management.