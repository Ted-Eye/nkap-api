from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Company(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    reggistered_by = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Ledger(models.Model):
    title = models.CharField(max_length=20, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.CharField(max_length=20, blank=True, null=True)
    reg_fee = models.IntegerField(default=0)
    mandatory_savings = models.IntegerField(verbose_name="Minimum savings upfront to access loans")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

class Client(models.Model):
    id = models.UUIDField(primary_key=True)
    ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    full_names = models.CharField(max_length=50)
    address = models.CharField(max_length=120)
    phone = models.CharField(max_length=12)
    occupation = models.CharField(max_length=20)
    account_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner
