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
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')
    
    return render(request, "register.html")

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    expenses = Expense.objects.all()
    return render(request, 'dashboard.html', {'expenses': expenses})

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        # Retrieve data from the form
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category_name = request.POST.get('category')
        
        try:
            # Try to retrieve the corresponding Category instance from the database
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            # If the category doesn't exist, show an error message
            messages.error(request, "The selected category does not exist.")
            return render(request, 'addexpense.html', context={})  # Render the form again
        
        # Create a new Expense record, associating it with the logged-in user
        Expense.objects.create(
            amount=amount,
            date=date,
            category=category,
            user=request.user  # Associate the expense with the logged-in user
        )
        
        # Add a success message without redirecting
        messages.success(request, "Expense added successfully!")
        
        # Render the form again, preserving the success message
        return render(request, 'addexpense.html')
    
    return render(request, 'addexpense.html')

@login_required
def manage_expense(request):
    # Query all expenses from the Expense model
    expenses = Expense.objects.all()
    
    # Pass expenses to the template
    return render(request, 'manage_expense.html', {'expenses': expenses})

@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id)  # This automatically handles missing expense
    
    # Fetch all categories to pass them to the template
    categories = Category.objects.all()

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('manage_expense')  # Redirect back to the manage_expenses page
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'edit_expense.html', {'form': form, 'expense': expense, 'categories': categories})

@login_required
def delete_expense(request, id):
    try:
        expense = Expense.objects.get(id=id)
    except Expense.DoesNotExist:
        raise Http404("Expense not found")
    
    if request.method == 'POST':
        expense.delete()
        return redirect('manage_expense')
    
    return render(request, 'delete_expense.html', {'expense': expense})

@login_required
def expense_report(request):
    today = timezone.now()
    
    # Filter logic based on the user's selection
    filter_type = request.GET.get('filter', 'today')  # Default to 'today'

    if filter_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        end_date = start_date + timedelta(days=6)  # End of the week (Sunday)
        expenses = Expense.objects.filter(date__range=[start_date, end_date])
    
    elif filter_type == 'monthly':
        start_date = today.replace(day=1)  # Start of the month
        end_date = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))  # End of the month
        expenses = Expense.objects.filter(date__range=[start_date, end_date])

    elif filter_type == 'yearly':
        start_date = today.replace(month=1, day=1)  # Start of the year
        end_date = today.replace(month=12, day=31)  # End of the year
        expenses = Expense.objects.filter(date__range=[start_date, end_date])

    else:  # 'today'
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)  # Start of today
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)  # End of today
        expenses = Expense.objects.filter(date__range=[start_date, end_date])

    context = {
        'expenses': expenses,
        'filter': filter_type,
    }
    return render(request, 'expense_report.html', context)


@login_required
def get_expense_data(request):
    # Filter expenses for a specific period or get all expenses
    expenses = Expense.objects.all()
    categories = {}
    
    # Categorize or aggregate expenses by category (or any logic you prefer)
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
def get_monthly_expenses(request):
    # Get current year and month
    current_year = timezone.now().year
    
    # Aggregate expenses by month for the current year
    expenses_by_month = Expense.objects.filter(date__year=current_year) \
        .values('date__month') \
        .annotate(total_expense=Sum('amount')) \
        .order_by('date__month')

    # Prepare data for the line chart
    months = [calendar.month_name[month['date__month']] for month in expenses_by_month]
    total_expenses = [month['total_expense'] for month in expenses_by_month]

    # Fill missing months with zero if no data for a month
    all_months = list(calendar.month_name[1:])
    for month in all_months:
        if month not in months:
            months.append(month)
            total_expenses.append(0)

    data = {
        'labels': months,
        'datasets': [{
            'label': 'Expenses by Month',
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