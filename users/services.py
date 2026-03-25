from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Wallet, Transaction, Preferences
from rest_framework import status
from rest_framework.exceptions import APIException

class InsufficientFunds(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient funds in wallet. Please check your balance and try again.'
    default_code = "insufficient_funds"
class UserNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail ='The provided username does not belong to any user! Please verify that you have entered the username correctly'
    default_code = 'user_not_found'

class UserDetail(User):
    class Meta:
        proxy = True
    def __str__(self):
        return f"name: {self.username } email: {self.email}"
    def info(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }
    

class WalletService:
    @staticmethod
    @transaction.atomic
    def rechargeWallet(user, targetId: str, amount: Decimal, note: str=""):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        mainAccount = get_object_or_404(Wallet, user=user, walletType='root')
        targetWallet = get_object_or_404(Wallet, user=user, id=targetId)

        # LOCK ROWS FOR UPDATE
        mainAccount = Wallet.objects.select_for_update().get(id=mainAccount.id)
        targetWallet = Wallet.objects.select_for_update().get(id=targetWallet.id)

        if mainAccount.accountBalance < amount:
            raise InsufficientFunds()
        
        mainAccount.accountBalance -= amount
        targetWallet.accountBalance += amount
        mainAccount.save(update_fields=["accountBalance"])
        targetWallet.save(update_fields=["accountBalance"])

        Transaction.objects.create(
            user=user,
            wallet=mainAccount, amount=-amount,
            transactionType=Transaction.DEBIT,
            note=note or f"Recharge to {targetWallet.title}",
            counterpartyWallet=targetWallet
        )
        # Transaction.objects.create(
        #     user=user,
        #     wallet=targetWallet, amount=amount,
        #     transactionType=Transaction.CREDIT,
        #     note=note or "Recharge from main account",
        #     counterpartyWallet=mainAccount
        # )

    @staticmethod
    @transaction.atomic
    def sendMoney (sender, origin_id: str, receiver_name,  amount: Decimal, dest_id: str='',  note: str=''):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        receiver = get_object_or_404(UserDetail, username=receiver_name)
        sender_wallet = get_object_or_404(Wallet, user=sender, id=origin_id)
        if dest_id == "":
            receiver_wallet = get_object_or_404(Wallet, user=receiver, walletType='root')

        else:
            receiver_wallet = get_object_or_404(Wallet, user=receiver, id=dest_id)
        prefs = Preferences.objects.get(user=sender) 
        currency = prefs.currency
        
        
        # LOCK FOR UPDATE
        sender_wallet = Wallet.objects.select_for_update().get(id=sender_wallet.id)
        receiver_wallet = Wallet.objects.select_for_update().get(id=receiver_wallet.id)
        

        if sender_wallet.accountBalance < amount:
            raise InsufficientFunds()
        sender_wallet.accountBalance-=amount
        receiver_wallet.accountBalance+=amount
        sender_wallet.save(update_fields=["accountBalance"])
        receiver_wallet.save(update_fields=["accountBalance"])

        
        Transaction.objects.create(
            user=sender,
            wallet=sender_wallet, amount=-amount,
            transactionType=Transaction.DEBIT,
            # note=note or f"You sent: {currency } {amount} to {receiver.username}",
            note=note or f"Sent: {amount } to {receiver.username}",
            counterpartyWallet=receiver_wallet,
            counterparty = UserDetail.info(receiver)
        )
        sender = get_object_or_404(UserDetail, id=sender.id)
        Transaction.objects.create(
            user=receiver,
            wallet=receiver_wallet, amount=amount,
            transactionType=Transaction.CREDIT,
            note=note or f"You received {currency } {amount} from {sender.username}",
            counterpartyWallet=sender_wallet,
            counterparty = UserDetail.info(sender)
        )