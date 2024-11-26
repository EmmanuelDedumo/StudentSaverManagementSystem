# EAD_ExpenseSystem/urls.py

from django.urls import path
from .views import (
    login_view, home_view, dashboard_view, add_expense, register_view, 
    logout_view, profile_view, delete_expense, manage_expenses, update_expense, expense_report,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),  # Changed path to avoid duplication
    path('dashboard/', dashboard_view, name='dashboard'),
    path('add-expense/', add_expense, name='add_expense'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('edit-expense/<int:expense_id>/', update_expense, name='edit_expense'),  # Added view function for updating
    path('delete-expense/<int:expense_id>/', delete_expense, name='delete_expense'),
    path('manage-expenses/', manage_expenses, name='manage_expenses'),
    path('expense-report/', expense_report, name='expense_report'),

]