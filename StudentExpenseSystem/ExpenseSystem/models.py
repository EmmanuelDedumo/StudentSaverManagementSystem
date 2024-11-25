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
    FUND_SOURCE_CHOICES = [
        ('e-wallet', 'E-Wallet'),
        ('bank', 'Bank'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fund_source = models.CharField(max_length=20, choices=FUND_SOURCE_CHOICES)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
