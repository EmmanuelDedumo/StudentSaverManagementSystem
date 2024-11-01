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
    1. Import the include() function: from django.urls import include, pathSSSS
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# StudentExpenseSystem/urls.py or EAD_StudentExpenseSysem/urls.py (if you have one)
 
# StudentExpenseSystem/urls.py or EAD_StudentExpenseSysem/urls.py
 
# StudentExpenseSystem/urls.py or EAD_StudentExpenseSysem/urls.py
 
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from EAD_ExpenseSystem.views import (
    login_view, logout_view, register_view, dashboard_view, 
    profile_view, add_expense, manage_expenses
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login/')),  # Redirect root URL to login
    path('login/', login_view, name='login'),
    path('login/', include('EAD_ExpenseSystem.urls')),  # Includes app URLs
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('add-expense/', add_expense, name='add_expense'),
    path('manage-expenses/', manage_expenses, name='manage_expenses'),

]