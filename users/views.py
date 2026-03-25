from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from .models import Preferences, Wallet, Transaction
from .services import WalletService, InsufficientFunds, UserNotFound
from rest_framework import generics, status
from rest_framework.views import APIView
from .serializers import UserSerializer, WalletSerializer, TransactionSerializer, LoginSerializer, PreferencesSerializer, RechargeSerializer, SendMoneySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class PreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = PreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:             
            return self.request.user.preferences.all()[0]
        except (Preferences.DoesNotExist, IndexError):
            return None

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(username=user.username)

class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    # Implement login logic here (e.g., using JWT or session authentication)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Add authentication logic here
        user = authenticate(
            username=serializer.validated_data['username'], 
            password=serializer.validated_data['password']
        )
        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        return Response({"message": "Login successful", "token": token.key})

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class WalletCreateView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
        # return Wallet.objects.filter(user=use)
        
        # return Wallet.objects.filter(user=self.request.user)
    def get_queryset(self):
        user = self.request.user
        return Wallet.objects.filter(user=user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
class WalletsUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Wallet.objects.filter(user=user)
    # def destroy(self, request, args, kwargs):
    #     print('USER:', request.user)
    #     print('kwargs:', kwargs)
    #     print('QUERYSET:', self.get_queryset())
    #     return
        
# class WalletListView(generics.ListAPIView):
#     serializer_class = WalletSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Wallet.objects.filter(user=user)

# class ProfileView(generics.RetrieveUpdateAPIView):
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         return self.request.user.profile

class Transactions(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user)

    def perform_create(self, serializer): 
        serializer.save(user=self.request.user, status='Completed')

class ReachargeWallet(APIView):
    def post(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            WalletService.rechargeWallet(
                user=request.user,
                targetId=serializer.validated_data["targetId"],
                amount=serializer.validated_data["amount"],
                note=serializer.validated_data.get("note")
            )
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except (InsufficientFunds) as e:

            data = {'ERROR': 'Insuficient funds'}
            # print({'ERROR': str(e)})
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
            # return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SendMoney(APIView):
    def get_queryset(self):
        user = self.request.user
        return Transactions.objects.filter(user=user)
    def post(self, request):
        serializer = SendMoneySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            WalletService.sendMoney(
                sender=request.user,
                origin_id=serializer.validated_data["origin_id"],
                receiver_name=serializer.validated_data["receiver_name"],
                amount=serializer.validated_data["amount"],
                dest_id=serializer.validated_data["dest_id"],
                note=serializer.validated_data["note"]
            )
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except(InsufficientFunds, UserNotFound) as e:
            return Response({'error': str(e)}, status=e.status_code)
            
