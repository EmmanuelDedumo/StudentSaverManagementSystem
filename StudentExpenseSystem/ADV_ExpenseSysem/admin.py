from django.contrib import admin
from .models import Expense  # Adjust the import according to your model's location

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'category')  # Specify which fields to display in the admin list view
    search_fields = ('category',)  # Add search functionality based on the category
    list_filter = ('date', 'category')  # Add filters for the list view

# Register the Expense model with the admin site
admin.site.register(Expense, ExpenseAdmin)
