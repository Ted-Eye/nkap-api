import uuid
from django.db import models
from django.contrib.auth.models import User


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
#     tel = models.CharField(max_length=15, unique=True)
#     profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
#     bio = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username}'s profile"

# class CashHub(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cash_hub")
#     title = models.CharField(max_length=100, default='Hub')
#     accountBalance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     transactions = models.JSONField(default=list, blank=True)
#     def __str__(self):
#         return f'{self.title } -Balance: {self.accountBalance}'
    
class Wallet(models.Model):
    WALLET_CHOICES = (
        ('root', 'root'),
        ('standard', 'standard'),
        ('vault', 'vault'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # id = models.CharField(max_length=250, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets', verbose_name='Owner')
    title = models.CharField(max_length=100)
    accountBalance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthlyLimit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transactions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    walletType = models.CharField(max_length=10, choices=WALLET_CHOICES, default='standard')
    status = models.CharField(max_length=10, default='active')

    def __str__(self):
        return f"{self.title} - Balance: {self.accountBalance}"
    def getCurrency(self):
        preferences = self.user.preferences.first()
        return preferences.currency if preferences else 'CFA'
    
class Transaction(models.Model):
    DEBIT = 'Send'
    CREDIT = 'Receive'
    TYPE_CHOICES = (
        ('Send', 'Cash-out'),
        ('Receive', 'Cash-in'),
    )
    EXPENSE_CHOICES = (
        ('rent', 'Rent'),
        ('shopping', 'Shopping'),
        ('medicals', 'Medicals'),
        ('ceremony', 'Ceremony'),
        ('others', 'Others'),
        
    )
    REVENUE_CHOICES = (
        ('salary', 'Salary'),
        ('business', 'Business'),
        ('investment', 'Investment'),
        ('gift', 'Gift'),
        ('others', 'Others'),
        ('recharge', 'Recharge')
    )
    ALL_CHOICES = EXPENSE_CHOICES + REVENUE_CHOICES
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', default=None)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='wallet_transactions')
    # walletID = models.CharField(max_length=150, default='abd1-234-567890')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transactionType = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Send')
    motive = models.CharField(max_length=50, choices=ALL_CHOICES, default='recharge') # INCLUDE DEFAULT VALUE TO TEST THE TURPLE VALUE REPRESENTATIONS
    counterpartyWallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    counterparty = models.CharField(max_length=150, null=True, blank=False)
    currency = models.CharField(max_length=10, default='CFA')
    note = models.CharField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, default='Completed')

    class Meta:
        ordering = ["-timestamp"]

class Preferences(models.Model):
    CURRENCIES = (
        ('cfa', 'CFA'),
        ('usd', 'USD'),
    )
    LANGUAGES = (
        ('english', 'En'),
        ('french', 'Fr')
    )
    THEMES = (
        ('LIGHT', 'light'),
        ('DARK', 'dark'),
        ('SYSTEM', 'system')
    )
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences')
    currency=models.CharField(max_length=10, choices=CURRENCIES, default='CFA')
    language=models.CharField(max_length=10, choices=LANGUAGES, default='En')
    theme=models.CharField(max_length=10, choices=THEMES, default='LIGHT')