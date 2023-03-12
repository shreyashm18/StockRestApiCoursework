from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
# from requests import Response
from rest_framework.response import Response


from userClients.models import UserClient, UserCurrency, UserSharesData
from userClients.serializers import UserCurrencySerializer, UserStocksSerializer
from rest_framework.views import APIView



def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login-user'))
    return render(request, 'index.html')

def profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login-user'))
    return render(request, 'user_profile.html')


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home-page'))
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if request.GET.get('next', None):
                return HttpResponseRedirect(request.GET['next'])
            return HttpResponseRedirect(reverse('home-page'))
        else:
            print('wrong user credentials')
            context["error"] = "Provide valid credentials !!"
            return render(request, "login.html", context)
    else:
        return render(request, "login.html", context)

def user_logout(request):
    if request.user.is_authenticated:
        print(f'user is logged in....')
        logout(request)
        return HttpResponseRedirect(reverse('login-user'))
    else:
        print(f'user is not logged in***')
        return HttpResponseRedirect(reverse('home-page'))
    
class UserShareList(APIView):

    def get(self,request,*args, **kwargs):
        # if request.user.is_authenticated:
            
        current_user = request.user.id
        user_data = UserClient.objects.get(user_id=current_user)
        user_shares = UserSharesData.objects.filter(username_id=user_data.id)
        print(user_shares)
        
        serializer = UserStocksSerializer(user_shares, many=True)
        return Response(serializer.data, status=200)
        # else:
        #     return HttpResponseRedirect(reverse('login-user'))
class UserCurrencyList(APIView):

    def get(self,request,*args, **kwargs):
        # if request.user.is_authenticated:
            
        current_user = request.user.id
        user_data = UserClient.objects.get(user_id=current_user)
        user_currency = UserCurrency.objects.filter(username_id=user_data.id)
        print(user_currency)
        
        serializer = UserCurrencySerializer(user_currency, many=True)
        base_fund = {"currency_name": "Great British Pound",
                    "currency_symbol": "GBP",
                    "funds": user_data.funds}
        data = serializer.data
        data.append(base_fund)
        print(data)
        return Response(data, status=200)
