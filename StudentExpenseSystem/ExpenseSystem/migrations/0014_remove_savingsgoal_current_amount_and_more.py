# Generated by Django 5.1.3 on 2024-12-08 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ExpenseSystem', '0013_savingsgoal_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='savingsgoal',
            name='current_amount',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='user',
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='current_savings',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='savingsgoal',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
