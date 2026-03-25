from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wallet, Preferences

@receiver(post_save, sender=User)
def create_user_wallets_and_prefs(sender, instance, created, **kwargs):
    if created:
        Preferences.objects.create(user=instance) # Create default preferences for the user
        
        # MAIN ACCOUNT TO THAT HANDLES ENTRY AND EXIT OF FUNDS AND FUNDING OF WALLETS
        Wallet.objects.create(user=instance, title='Hub', walletType='root')

        # WALLETS ASSOCIATED TO EVERY USER THAT SIGNS UP TO THE APPLICATION
        default_wallets = ["Personal", "Savings", "Business"]
        for title in default_wallets:
            Wallet.objects.create(user=instance, title=title)
        

# @receiver(post_save, sender=User)
# def create_user_hub(sender, instance, created, **kwargs):
#     if created:
#         CashHub.objects.create(user=instance, title='Hub')

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#             UserProfile.objects.create(user=instance)