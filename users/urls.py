from django.urls import path
from .views import UserDetailView, WalletCreateView, UserCreateView, UserLoginView, WalletsUpdateView, UserListView, Transactions, PreferencesView, ReachargeWallet, SendMoney

urlpatterns = [
    path("", UserCreateView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("me/", UserListView.as_view(), name='user'),
    # path("me/profile/", ProfileView.as_view(), name="user-profile"),
    path("<int:use_id>/", UserDetailView.as_view(), name="user-detail"),
    path("wallets/", WalletCreateView.as_view(), name="wallet-list"),
    path("wallets/<uuid:pk>/", WalletsUpdateView.as_view(), name="wallet-detail"),
    path("transactions/", Transactions.as_view(), name="transaction"),
    path("recharge/", ReachargeWallet.as_view(), name='recharge'),
    path("send/", SendMoney.as_view(), name='send_money'),
    path("preferences/", PreferencesView.as_view(), name="preferences/"),
]