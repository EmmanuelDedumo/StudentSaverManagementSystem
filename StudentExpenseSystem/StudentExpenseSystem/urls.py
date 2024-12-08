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
# StudentExpenseSystem/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from ExpenseSystem import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ExpenseSystem/', include('ExpenseSystem.urls')),  # Routes to ExpenseSystem app
    path('login/', views.login_view, name='login'),  # Use a view for login
    path('', lambda request: redirect('login')),  # Redirect root to login
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit_expense/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete_expense/<int:id>/', views.delete_expense, name='delete_expense'),
    path('savings/', views.savings_dashboard, name='savings_dashboard'),
    path('deposit/', views.deposit_savings, name='deposit_savings'),
    path('edit-savings-goal/<int:goal_id>/', views.edit_savings_goal, name='edit_savings_goal'),
    path('delete-savings-goal/<int:goal_id>/', views.delete_savings_goal, name='delete_savings_goal'),
    path('delete-profile-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('goal/<int:goal_id>/delete/', views.delete_savings_goal, name='delete_savings_goal'),
]

# Add media URL pattern to serve uploaded media during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

