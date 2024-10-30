# ADV_ExpenseSysem/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import UserRegistrationForm  
from django.utils import timezone
from .models import Expense  # Assuming an Expense model exists
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm  # Make sure to create a form for expenses


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')  # Redirect to login page after registration
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    return render(request, 'dashboard.html', {'user': request.user})



@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()  # Save the expense to the database
            return redirect('manage_expenses')  # Redirect to the list of expenses
    else:
        form = ExpenseForm()
    return render(request, 'addexpense.html', {'form': form})


@login_required
def update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'update_expense.html', {'form': form})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    return redirect('dashboard')


def manage_expenses(request):
    expenses = Expense.objects.all()  # Fetch all expenses
    return render(request, 'manage_expenses.html', {'expenses': expenses})

def logout_view(request):
    logout(request)
    return redirect('login') 
