from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.EmailField()  # This should be email_address, not "email address"

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)  # Add the description field

    def __str__(self):
        return f"Expense {self.id} - {self.amount} - {self.date}"



class Savings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_income = models.FloatField(default=0.00)
    total_expense = models.FloatField(default=0.00)
    current_savings = models.FloatField(default=0.00)

    @property
    def balance(self):
        return self.total_income - self.total_expense  # Calculate balance dynamically

    def __str__(self):
        return f"{self.user.username}'s Savings"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default_profile.png')

    def __str__(self):
        return f'{self.user.username} Profile'
    
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    completed = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True) 
