# apps.py
from django.apps import AppConfig

class ExpenseSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ExpenseSystem'

    def ready(self):
        import ExpenseSystem.signals  # Ensure signals are imported
