"""
URL configuration for StudentExpenseSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.shortcuts import redirect
from ExpenseSystem import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ExpenseSystem/', include('ExpenseSystem.urls')),
    path('login/', include('ExpenseSystem.urls')),  # Make sure login is defined in ExpenseSystem.urls
    path('', lambda request: redirect('login')),  # Redirect root URL to login
    path('register/', views.register_view, name='register'),  # New registration path
    path('dashboard/', views.dashboard, name='dashboard'),
    path('savings/', views.savings_dashboard, name='savings_dashboard'),
    path('deposit/', views.deposit_savings, name='deposit_savings'),
    
]
