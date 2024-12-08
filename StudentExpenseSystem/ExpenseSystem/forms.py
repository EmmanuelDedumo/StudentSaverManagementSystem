# ExpenseSystem/forms.py

from django import forms
from ExpenseSystem.models import Expense, UserProfile  # Make sure you import the Expense model
from django.contrib.auth.models import User
from .models import SavingsGoal

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'category']  # Include description here


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']       

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label="Deposit Amount")

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'description']

class TransferForm(forms.Form):
    recipient_name = forms.CharField(max_length=255, label="Recipient Name")
    amount = forms.FloatField(min_value=0.01, label="Transfer Amount")
    notes = forms.CharField(widget=forms.Textarea, required=False, label="Notes")

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")