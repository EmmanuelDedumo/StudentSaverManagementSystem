from django.urls import path
from ExpenseSystem import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('manage_expense/', views.manage_expense, name='manage_expense'),
    path('edit_expense/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete_expense/<int:id>/', views.delete_expense, name='delete_expense'),
    path('expense-report/', views.expense_report, name='expense_report'),
    path('get-expense-data/', views.get_expense_data, name='get_expense_data'),
    path('date-expenses/', views.get_expenses_by_date, name='get_expenses_by_date'),
    path('profile/', views.user_profile, name='user_profile'),
    path('savings/', views.savings_dashboard, name='savings_dashboard'),
    path('deposit/', views.deposit_savings, name='deposit_savings'),
    path('add-savings-goal/', views.add_savings_goal, name='add_savings_goal'),
    path('delete-profile-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('save-savings-goal/', views.save_savings_goal, name='save_savings_goal'),
    path('edit-savings-goal/<int:goal_id>/', views.edit_savings_goal, name='edit_savings_goal'),
    path('delete-savings-goal/<int:goal_id>/', views.delete_savings_goal, name='delete_savings_goal'),
    path('goal/<int:goal_id>/delete/', views.delete_savings_goal, name='delete_savings_goal'),
    path('transfer/', views.transfer_savings, name='transfer_savings'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
