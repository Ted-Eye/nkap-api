from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Wallet, Transaction, Preferences

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        fields = ('username', 'password') 
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# class HubSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CashHub
#         fields = '__all__'
#         read_only_fields = ('user')

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'
        read_only_fields = ('user',)

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'id', 'user', 'accountBalance', 'status', 'transactions')
        extra_kwargs = {
            'user': {'read_only': True}
        }
    def create(self, validated_data):
        return Wallet.objects.create(**validated_data) 

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('user', 'id', 'currency', 'status', 'timestamp')
    
    def validate_wallet(self, wallet):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError("Request context is required.")
        if wallet.user_id != request.user.id:
            raise serializers.ValidationError("Cannot perform transactions on another user's wallet.")
        # if wallet.status != 'active':
        #     raise serializers.ValidationError("Cannot perform transactions on an inactive wallet.")
        return wallet
    
    def create(self, validated_data):
        wallet = validated_data["wallet"]
        # walletID = validated_data["walletID"]
        transactionType = validated_data["transactionType"]
        amount = validated_data["amount"]

        with transaction.atomic():
            if transactionType == Transaction.DEBIT:
                if wallet.accountBalance < amount:
                    raise serializers.ValidationError("Insufficient balance")
                wallet.accountBalance -= amount
            else:
                wallet.accountBalance += amount

            wallet.save(update_fields=['accountBalance'])
            # return super().create(validated_data)
            return Transaction.objects.create(**validated_data)    


# HANDLE REACHARGE OF REGULAR WALLETS FROM MAIN USER ACCOUNT
class RechargeSerializer(serializers.Serializer):
    targetId = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=5)
    note=serializers.CharField(required=False, allow_blank=True)

class SendMoneySerializer(serializers.Serializer):
    origin_id = serializers.CharField()
    receiver_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=5)
    dest_id = serializers.CharField(required=False, allow_blank=True)
    note=serializers.CharField(required=False, allow_blank=True)

# class UserProfileSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source='user.first_name', required=False)
#     last_name = serializers.CharField(source='user.last_name', required=False)
#     email = serializers.EmailField(source='user.email', required=False)

#     class Meta:
#         model = Profile
#         fields = ['first_name', 'last_name', 'tel', 'email', 'bio', 'profile_picture']
#         read_only_fields = ('user',)

#     def create(self, validated_data):
#         user_data = validated_data.pop('user', None)
#         request_user = None
#         # if called from a view with authentication, associate to request.user
#         if self.context.get('request') and hasattr(self.context['request'], 'user'):
#             request_user = self.context['request'].user

#         profile = Profile.objects.create(**validated_data, user=request_user)

#         if user_data and profile.user:
#             for attr, value in user_data.items():
#                 setattr(profile.user, attr, value)
#             profile.user.save()

#         return profile

#     def update(self, instance, validated_data):
#         user_data = validated_data.pop('user', None)
#         instance = super().update(instance, validated_data)
#         if user_data:
#             for attr, value in user_data.items():
#                 setattr(instance.user, attr, value)
#             instance.user.save()
#         return instance