"""
URL configuration for retailshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app import views 

urlpatterns = [
    path('admin/', admin.site.urls),   
    path('', include('app.urls')),
]
# Change the Admin page title (the text in the browser tab)
admin.site.site_title = "Jersar RetailShop Admin Portal" 

# Change the main Admin header text (the large text at the top of the page)
admin.site.site_header = "Jersar RetailShop Management System"

# Change the text for the login page (optional, usually "Site Administration")
admin.site.index_title = "Welcome to the Jersar RetailShop Administration" 

