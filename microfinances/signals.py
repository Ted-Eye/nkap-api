from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Company, Ledger

@receiver(post_save, sender=Company)
def create_savings_ledger(sender, instance, created, **kwargs):
    if created:
        # DEFAULT SAVINGS LEDGER UPON MFI REGISTRATION
        Ledger.objects.create(user=instance,   title='Daily collects')