from django.shortcuts import render, redirect, get_object_or_404
from ExpenseSystem.models import Expense, Savings, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from ExpenseSystem.models import Expense
from ExpenseSystem.forms import ExpenseForm
from django.http import Http404
from ExpenseSystem.forms import UserProfileForm
from ExpenseSystem.models import UserProfile
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
import calendar
from django.db.models import Sum
from django.utils import timezone
from .models import Savings
from .forms import DepositForm



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate and log the user in
            user = form.get_user()
            login(request, user)
            # Redirect to the dashboard after login
            return redirect('dashboard')  # Ensure 'dashboard' is the correct URL name
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, "register.html")
        
        # Create user
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')
    
    return render(request, "register.html")

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    expenses = Expense.objects.all()
    return render(request, 'dashboard.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category_id = request.POST.get('category')
        
        try:
            # Get the category by its ID
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, 'Category not found.')
            return redirect('add_expense')  # Redirect back to add_expense page if category is invalid
        
        # Create or retrieve the expense for the current user
        expense, created = Expense.objects.get_or_create(
            user=request.user,
            amount=amount,
            date=date,
            category=category
        )
        
        if created:
            messages.success(request, 'Expense added successfully!')
        else:
            messages.warning(request, 'This expense already exists.')

        return redirect('manage_expense')  # Redirect to the expense management page

    categories = Category.objects.all()  # Retrieve all categories for the select dropdown
    return render(request, 'addexpense.html', {'categories': categories})


@login_required
def manage_expense(request):
    # Retrieve all expenses for the current user
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'manage_expense.html', {'expenses': expenses})

@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)  # Ensure the user owns the expense
    
    # Fetch all categories to pass them to the template
    categories = Category.objects.all()

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('manage_expense')  # Redirect back to the manage_expenses page
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'edit_expense.html', {'form': form, 'expense': expense, 'categories': categories})

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)  # Ensure the user owns the expense
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('manage_expenses')
    
    return render(request, 'delete_expense.html', {'expense': expense})

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from .models import Expense  # Make sure to import your Expense model

@login_required
def expense_report(request):
    today = timezone.now()

    # Filter logic based on the user's selection
    filter_type = request.GET.get('filter', 'today')  # Default to 'today'

    # Filter expenses based on the logged-in user
    user_expenses = Expense.objects.filter(user=request.user)

    if filter_type == 'weekly':
        # Calculate the most recent Sunday
        start_date = today - timedelta(days=today.weekday() + 1)  # Sunday
        end_date = start_date + timedelta(days=6)  # End of the week (Saturday)
        expenses = user_expenses.filter(date__range=[start_date, end_date])

    elif filter_type == 'monthly':
        start_date = today.replace(day=1)  # Start of the month
        end_date = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))  # End of the month
        expenses = user_expenses.filter(date__range=[start_date, end_date])

    elif filter_type == 'yearly':
        start_date = today.replace(month=1, day=1)  # Start of the year
        end_date = today.replace(month=12, day=31)  # End of the year
        expenses = user_expenses.filter(date__range=[start_date, end_date])

    else:  # 'today'
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)  # Start of today
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)  # End of today
        expenses = user_expenses.filter(date__range=[start_date, end_date])

    context = {
        'expenses': expenses,
        'filter': filter_type,
    }
    return render(request, 'expense_report.html', context)


@login_required
def get_expense_data(request):
    # Filter expenses for the logged-in user
    expenses = Expense.objects.filter(user=request.user)
    categories = {}

    # Categorize or aggregate expenses by category
    for expense in expenses:
        if expense.category.name not in categories:
            categories[expense.category.name] = 0
        categories[expense.category.name] += expense.amount

    # Prepare data for the chart
    data = {
        'labels': list(categories.keys()),  # Categories
        'datasets': [{
            'label': 'Expenses',
            'data': list(categories.values()),  # Amounts per category
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',  # Color for the chart bars
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }

    return JsonResponse(data)


@login_required
def get_expenses_by_date(request):
    # Fetch expenses for the logged-in user, grouped by the exact date
    expenses_by_date = Expense.objects.filter(user=request.user) \
        .values('date') \
        .annotate(total_expense=Sum('amount')) \
        .order_by('date')  # Order by date to get chronological order

    # Prepare data for the chart
    dates = [expense['date'].strftime('%Y-%m-%d') for expense in expenses_by_date]
    total_expenses = [expense['total_expense'] for expense in expenses_by_date]

    data = {
        'labels': dates,
        'datasets': [{
            'label': 'Expenses by Date',
            'data': total_expenses,
            'fill': False,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'tension': 0.1
        }]
    }
    return JsonResponse(data)



@login_required
def user_profile(request):
    if request.method == "POST":
        # Get the current user
        user = request.user

        # Update user details
        user.username = request.POST.get("username")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile.profile_picture = request.FILES['profile_picture']
            user.profile.save()

        # Handle password change
        if request.POST.get("password"):
            user.set_password(request.POST.get("password"))
            user.save()

        # Save user details
        user.save()

        return redirect('user_profile')  # Redirect to the same page after saving

    return render(request, 'user_profile.html')

def savings_dashboard(request):
    # Retrieve or create the savings object for the current user
    savings, created = Savings.objects.get_or_create(
        user=request.user,
        defaults={
            'total_income': 0.0,
            'total_expense': 0.0,
            'current_savings': 0.0
        }
    )

    # Handle POST requests for deposit or transfer actions
    if request.method == "POST":
        action = request.POST.get('action')  # Either 'deposit' or 'transfer'
        try:
            amount = float(request.POST.get('amount', 0))
        except ValueError:
            return render(request, 'savings.html', {
                'savings': savings,
                'error': "Invalid amount entered."
            })

        if action == 'deposit':
            savings.total_income += amount  # Add deposit amount to total_income
        elif action == 'transfer':
            if savings.current_savings >= amount:
                savings.total_expense += amount  # Add amount to total_expense for transfers
            else:
                return render(request, 'savings.html', {
                    'savings': savings,
                    'error': "Insufficient savings for transfer."
                })

        # Update current_savings based on income and expense
        savings.current_savings = savings.total_income - savings.total_expense
        savings.save()  # Save updates

        return redirect('savings_dashboard')  # Refresh page after changes

    return render(request, 'savings.html', {'savings': savings})



def deposit_savings(request):
    # Retrieve the user's savings object
    savings = Savings.objects.get(user=request.user)
    
    if request.method == "POST":
        action = request.POST.get('action')
        amount = request.POST.get('amount')

        try:
            # Convert the amount to a float and round it to two decimal places
            amount = float(amount)
            amount = round(amount, 2)  # Round to 2 decimal places for precision

            if action == 'deposit':
                savings.total_income += amount
            elif action == 'transfer':
                if savings.current_savings >= amount:
                    savings.current_savings -= amount
                else:
                    return render(request, 'savings.html', {
                        'savings': savings,
                        'error': "Insufficient savings for transfer."
                    })
            
            # Recalculate current savings based on income and expenses
            savings.current_savings = savings.total_income - savings.total_expense
            savings.save()
            
            # After deposit, redirect back to the savings dashboard
            return redirect('savings_dashboard')

        except ValueError:
            return render(request, 'deposit_savings.html', {
                'savings': savings,
                'error': "Invalid amount entered. Please enter a valid number."
            })
    
    return render(request, 'deposit_savings.html', {'savings': savings})  # Render deposit page

