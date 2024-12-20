from django.shortcuts import render, redirect, get_object_or_404
import requests
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
from .models import Profile
from django.core.files.base import ContentFile
from .utils import save_profile_picture_from_url
from io import BytesIO
import logging
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .forms import SavingsGoalForm, ForgotPasswordForm, ResetPasswordForm
from .models import SavingsGoal
from decimal import Decimal
from django.http import HttpResponse
from .forms import TransferForm  # Assuming you have a form for transferring funds
from django.db import transaction
from django import forms



def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                # Username exists, redirect to reset password page
                return redirect('reset_password', user_id=user.id)
            except User.DoesNotExist:
                messages.error(request, "Username does not exist.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


def reset_password(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                user.set_password(new_password)  # Set the new password
                user.save()
                messages.success(request, "Password reset successfully!")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form})



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
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
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

        # Create user with first name and last name
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        messages.success(request, "Account created successfully. Please log in.")
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

        return redirect('dashboard')  # Redirect to the expense management page

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
        return redirect('manage_expense')
    
    return render(request, 'delete_expense.html', {'expense': expense})


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
        _, last_day = calendar.monthrange(today.year, today.month)  # Get the last day of the month
        end_date = today.replace(day=last_day)  # End of the month
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

logger = logging.getLogger(__name__)

from django.http import JsonResponse

@login_required
def user_profile(request):
    if request.method == 'POST':
        # Get the user profile
        user_profile = request.user.profile

        # Check for delete profile picture
        if 'delete_profile_picture' in request.POST:
            if user_profile.profile_picture:
                picture_path = user_profile.profile_picture.path
                if default_storage.exists(picture_path):
                    default_storage.delete(picture_path)
                user_profile.profile_picture = None
                user_profile.save()
            return JsonResponse({'status': 'success', 'message': 'Profile picture deleted and reset'})

        # Update profile details
        request.user.username = request.POST.get('username', request.user.username)
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)

        if password := request.POST.get('password'):
            request.user.set_password(password)

        if profile_picture := request.FILES.get('profile_picture'):
            user_profile.profile_picture = profile_picture

        request.user.save()
        user_profile.save()
        return redirect('user_profile')

    # Render profile page with user details pre-filled
    return render(request, 'user_profile.html', {
        'user': request.user
    })

def save_profile_picture_from_url(user, image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        # Extract the file name from the URL
        file_name = image_url.split("/")[-1]
        # Save the image to the user's profile
        user.profile.profile_picture.save(file_name, ContentFile(response.content), save=True)


@login_required
def delete_profile_picture(request):
    if request.method == "POST":
        profile = request.user.profile  # Access the user's profile
        profile.profile_picture.delete(save=False)  # Delete the current picture file
        profile.profile_picture = None  # Reset to None
        profile.save()  # Save the changes
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request method"}, status=400)



@login_required
def savings_dashboard(request):
    # Get or create the user's savings object
    savings, created = Savings.objects.get_or_create(
        user=request.user,
        defaults={'total_income': 0.0, 'total_expense': 0.0, 'current_savings': 0.0}
    )
    savings_goals = SavingsGoal.objects.filter(user=request.user)

    return render(request, 'savings.html', {'savings': savings, 'savings_goals': savings_goals})



def deposit_savings(request):
    savings = Savings.objects.get(user=request.user)

    if request.method == "POST":
        action = request.POST.get('action')
        amount = request.POST.get('amount')

        try:
            amount = float(amount)
            amount = round(amount, 2)

            if action == 'deposit':
                savings.total_income += amount  # Add to total income
                savings.current_savings += amount  # Add to current savings
            elif action == 'transfer':
                if savings.current_savings >= amount:
                    savings.current_savings -= amount
                else:
                    return render(request, 'savings.html', {
                        'savings': savings,
                        'error': "Insufficient savings for transfer."
                    })

            # Recalculate current savings based on income and expenses
            savings.save()

            return redirect('savings_dashboard')

        except ValueError:
            return render(request, 'deposit_savings.html', {
                'savings': savings,
                'error': "Invalid amount entered. Please enter a valid number."
            })
    return render(request, 'deposit_savings.html', {'savings': savings})




@login_required
def add_savings_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            savings_goal = form.save(commit=False)
            savings_goal.user = request.user  # Link the goal to the logged-in user
            savings_goal.save()
            return redirect('savings_dashboard')  # Redirect after saving
    else:
        form = SavingsGoalForm()

    return render(request, 'add_savings_goal.html', {'form': form})

def save_savings_goal(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')  # Corrected field name
        target_amount = request.POST.get('target_amount')
        description = request.POST.get('description')

        # Check if a goal is being updated or created
        goal_id = request.POST.get('goal_id')  # Assuming 'goal_id' is included in the form

        if goal_id:
            # Retrieve the existing goal and update it
            savings_goal = SavingsGoal.objects.get(id=goal_id)
            savings_goal.name = name
            savings_goal.target_amount = target_amount
            savings_goal.description = description
            # Do not modify the 'completed' field unless specified
            savings_goal.save()
        else:
            # Create a new savings goal
            savings_goal = SavingsGoal(
                name=name,
                target_amount=target_amount,
                description=description,
                user=request.user
            )
            savings_goal.save()

        # Redirect to the savings dashboard after saving
        return redirect('savings_dashboard')

    # Redirect back to the form if the request is not POST
    return redirect('add-savings-goal')


@login_required
def edit_savings_goal(request, goal_id):
    savings_goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)

    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=savings_goal)
        if form.is_valid():
            form.save()
            return redirect('savings_dashboard')  # Redirect after saving
    else:
        form = SavingsGoalForm(instance=savings_goal)
        form.fields['current_amount'].widget = forms.HiddenInput()  # Hide the field

    return render(request, 'edit_savings_goal.html', {'form': form, 'goal': savings_goal})



@login_required
def delete_savings_goal(request, goal_id):
    savings_goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        savings_goal.delete()
        return redirect('savings_dashboard')  # Redirect after deletion

    return redirect('savings_dashboard')  # Redirect if accessed without POST

@login_required
def transfer_savings(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            amount = Decimal(amount)  # Ensure amount is a Decimal

            goal_id = form.cleaned_data['goal_id']

            try:
                # Get the savings data for the current user and ensure it's a Decimal
                savings = Savings.objects.get(user=request.user)
                current_savings = Decimal(savings.current_savings)  # Convert current_savings to Decimal

                # Get the savings goal and check conditions
                goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)

                if amount < goal.target_amount:
                    return render(request, 'transfer_savings.html', {
                        'error': 'Insufficient funds.',
                        'form': form,
                        'savings_goals': SavingsGoal.objects.filter(user=request.user, completed=False)
                    })

                if current_savings < amount:
                    return render(request, 'transfer_savings.html', {
                        'error': 'Insufficient funds in your savings.',
                        'form': form,
                        'savings_goals': SavingsGoal.objects.filter(user=request.user, completed=False)
                    })

                with transaction.atomic():
                    # Update the savings goal
                    goal.current_amount += amount
                    if goal.current_amount >= goal.target_amount:
                        goal.completed = True
                    goal.save()

                    # Deduct the amount from current savings
                    savings.current_savings = current_savings - amount  # Ensure this is Decimal
                    savings.save()

                return redirect('savings_dashboard')

            except Savings.DoesNotExist:
                return render(request, 'transfer_savings.html', {
                    'error': 'User savings data not found',
                    'form': form,
                    'savings_goals': SavingsGoal.objects.filter(user=request.user, completed=False)
                })
            except SavingsGoal.DoesNotExist:
                return render(request, 'transfer_savings.html', {
                    'error': 'Savings goal not found',
                    'form': form,
                    'savings_goals': SavingsGoal.objects.filter(user=request.user, completed=False)
                })

    else:
        form = TransferForm()

    savings_goals = SavingsGoal.objects.filter(user=request.user, completed=False)
    return render(request, 'transfer_savings.html', {
        'form': form,
        'savings_goals': savings_goals
    })


@login_required
def get_savings_balance(request):
    try:
        savings = Savings.objects.get(user=request.user)
        return JsonResponse({'balance': float(savings.current_savings)}, status=200)
    except Savings.DoesNotExist:
        return JsonResponse({'error': 'Savings data not found'}, status=404)
