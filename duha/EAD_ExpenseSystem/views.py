# EAD_ExpenseSystem/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from .models import Expense  # Assuming an Expense model exists
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, UserRegistrationForm  # Ensure these forms are defined

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'user': request.user})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_expenses')
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

@login_required
def expense_report(request):
    expenses = Expense.objects.all().order_by('-date')  # Sort by date descending
    return render(request, 'expense_report.html', {'expenses': expenses})

@login_required
def manage_expenses(request):
    expenses = Expense.objects.all()
    return render(request, 'manage_expenses.html', {'expenses': expenses})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    return render(request, 'profile.html')

def expense_report(request):
    filtered_expenses = []
    if request.method == 'POST':
        report_type = request.POST.get('reportType')
        today = timezone.now().date()
        
        if report_type == 'today':
            filtered_expenses = Expense.objects.filter(date=today)
        elif report_type == 'yesterday':
            yesterday = today - timezone.timedelta(days=1)
            filtered_expenses = Expense.objects.filter(date=yesterday)
        elif report_type == 'week':
            start_of_week = today - timezone.timedelta(days=today.weekday())  # Monday
            filtered_expenses = Expense.objects.filter(date__gte=start_of_week)
        elif report_type == 'month':
            start_of_month = today.replace(day=1)
            filtered_expenses = Expense.objects.filter(date__gte=start_of_month)

    return render(request, 'expensereport.html', {'filtered_expenses': filtered_expenses})