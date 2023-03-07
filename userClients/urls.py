from django.urls import path

from .views import user_login, index, user_logout

urlpatterns = [
    path('', user_login, name="login-user"),
    path('home', index, name="home-page"),
    path('logout', user_logout, name="logout-user"),
]