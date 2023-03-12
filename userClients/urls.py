from django.urls import path

from .views import UserCurrencyList, UserShareList, profile, user_login, index, user_logout

urlpatterns = [
    path('', user_login, name="login-user"),
    path('home', index, name="home-page"),
    path('logout', user_logout, name="logout-user"),
    path('profile', profile, name="profile-user"),
    path('profileData', UserShareList.as_view(), name="user-data"),
    path('profileCurrency', UserCurrencyList.as_view(), name="user-currency"),


]