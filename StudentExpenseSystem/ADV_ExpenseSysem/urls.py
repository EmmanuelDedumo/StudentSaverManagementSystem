
# ADV_ExpenseSysem/urls.py

from django.urls import path
from .views import (
    login_view, home_view, dashboard_view, add_expense,
    register_view, logout_view,  edit_expense, delete_expense,
    manage_expenses  # Ensure this is imported
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),  
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('add-expense/', add_expense, name='add_expense'),
    path('edit_expense/<int:expense_id>/', edit_expense, name='edit_expense'),
    path('delete_expense/<int:expense_id>/', delete_expense, name='delete_expense'),
    path('manage-expenses/', manage_expenses, name='manage_expenses'),
]
