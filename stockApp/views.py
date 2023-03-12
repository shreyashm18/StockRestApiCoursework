import datetime
import json
import os
from enum import Enum


from django.core.exceptions import BadRequest
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from userClients.models import UserClient, UserCurrency, UserSharesData
from .models import SharesData
from .serializers import SharesListSerializer
import requests
from requests.structures import CaseInsensitiveDict


class ModelFilterFields(Enum):
    COMPANY_NAME = "company_name"
    COMPANY_SYMBOL = "company_symbol"

def apiOverView(request):
    return JsonResponse("API demo", safe=False)

def stockDetail(request, company_symbol):
    stock = SharesData.objects.get(company_symbol = company_symbol)
    current_user = request.user.id
    user_data = UserClient.objects.get(user_id=current_user)
    
    try:
        user_shares = UserSharesData.objects.get(username_id=user_data.id, company_symbol = stock.company_symbol)
        share_qty = user_shares.shares_qty
        
    except UserSharesData.DoesNotExist:
        share_qty = 0
    print(f'share_qty ========{share_qty}')
    context = {'data':stock, 'share_qty':share_qty}
    return render(request, 'stockDetail.html',context=context)

class ShareList(APIView):
    company_name = None
    company_symbol = None
    share_price = None
    quantity = None


    def get_queryset(self):
        queryset = SharesData.objects.all()
        self.company_name = self.request.query_params.get("company_name", None)
        self.company_symbol = self.request.query_params.get("company_symbol", None)
        self.share_price = self.request.query_params.get("share_price_filter", None)
        self.quantity = self.request.query_params.get("quantity_filter", None)
        # self.min_share_price = self.request.query_params.get("min_share_price", False)
        # self.min_quantity = self.request.query_params.get("min_quantity", False)



        if self.company_name:
            queryset = queryset.filter(company_name=self.company_name)
            return queryset
        elif self.company_symbol:
            queryset = queryset.filter(company_symbol=self.company_symbol)
            return queryset
        elif self.share_price:
            if self.share_price.lower() == "max":
                queryset = queryset.order_by('-share_price')[:1]
                return queryset
            elif self.share_price.lower() == "min":
                queryset = queryset.order_by('share_price')[:1]
                return queryset
        elif self.quantity:
            if self.quantity.lower() == "max":
                queryset = queryset.order_by('-no_of_shares')[:1]
                return queryset
            elif self.quantity.lower() == "min":
                queryset = queryset.order_by('no_of_shares')[:1]
                return queryset
        # elif self.min_share_price:
        #     queryset = queryset.order_by('share_price')[:1]
        #     return queryset
        # elif self.min_quantity:
        #     queryset = queryset.order_by('no_of_shares')[:1]
        #     return queryset
        else:
            return queryset


    def get(self,request,*args, **kwargs):
        if request.user.is_authenticated:
            
            if len(request.query_params) > 1:
                return Response("You cant pass more than 1 searching parameters in the request", status=400)
            shares = self.get_queryset()
            serializer = SharesListSerializer(shares, many=True)
            return Response(serializer.data, status=200)
        else:
            return HttpResponseRedirect(reverse('login-user'))

    def post(self,request):
        data=request.data
        print(data)
        shares=SharesListSerializer(data=data)
        if shares.is_valid():
            shares.save()
            return Response(shares.data,status=201)
        return Response(shares.errors,status=400)

class ShareChangePrice(APIView):
    def get_object(self, filter_by, filter_value):
        try:
            if filter_by == "company_name":
                return SharesData.objects.get(company_name = filter_value)
            elif filter_by == "company_symbol":
                return SharesData.objects.get(company_symbol = filter_value)
        except SharesData.DoesNotExist:
            raise Http404

    def get(self,request, *args, **kwargs):
        is_authorized: False
        if request.user.is_authenticated:

            current_user = request.user.id
            user_data = UserClient.objects.get(user_id=current_user)
            if user_data.is_admin:
                is_authorized=True
            else:
                is_authorized=False

            if is_authorized:    
                company_name = request.query_params.get('company_name', None)
                new_price = request.query_params.get('changeRate', None)
                company_symbol = request.query_params.get('company_symbol', None)
                filter_by = None
                filter_value = None
                raise_error = False
                if company_name:
                    filter_by = "company_name"
                    filter_value = company_name
                elif company_symbol:
                    filter_by = "company_symbol"
                    filter_value = company_symbol
                else:
                    raise_error = True

                if not raise_error:
                    instance = self.get_object(filter_by, filter_value)
                    if new_price:
                        instance.share_price = new_price
                        instance.save()
                        return Response("Price updated successfully")
                    else:
                        raise_error = True
                if raise_error:
                    raise BadRequest('Invalid request.')
            else:
                return Response("User is not authorisez to change price", status=401)
        else:
            return HttpResponseRedirect(reverse('login-user'))


class ShareUpdatQty(APIView):
    def get_object(self, filter_by, filter_value):
        try:
            if filter_by == "company_name":
                return SharesData.objects.get(company_name=filter_value)
            elif filter_by == "company_symbol":
                return SharesData.objects.get(company_symbol=filter_value)
        except SharesData.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        is_authorized: False
        if request.user.is_authenticated:

            current_user = request.user.id
            user_data = UserClient.objects.get(user_id=current_user)
            if user_data.is_admin:
                is_authorized=True
            else:
                is_authorized=False

            if is_authorized:
                company_name = request.query_params.get('company_name', None)
                quantity = request.query_params.get('quantity', None)
                company_symbol = request.query_params.get('company_symbol', None)
                filter_by = None
                filter_value = None
                raise_error = False
                if company_name:
                    filter_by = "company_name"
                    filter_value = company_name
                elif company_symbol:
                    filter_by = "company_symbol"
                    filter_value = company_symbol
                else:
                    raise_error = True

                if not raise_error:
                    instance = self.get_object(filter_by, filter_value)
                    if quantity:
                        instance.no_of_shares = quantity
                        instance.save()
                        return Response("Shares quantity updated successfully")
                    else:
                        raise_error = True
                if raise_error:
                    raise BadRequest('Invalid request.')
            else:
                return Response("User is not authorisez to change share quantity", status=401)
        else:
            return HttpResponseRedirect(reverse('login-user'))

class BuySellShares(APIView):
    company_name = None
    company_symbol = None

    def get_object(self):
        try:
            if self.company_symbol:
                return SharesData.objects.get(company_symbol = self.company_symbol)
            elif self.company_name:
                return SharesData.objects.get(company_name=self.company_name)

        except SharesData.DoesNotExist:
            raise Http404

    def get(self, request):
        if request.user.is_authenticated:
            self.company_name = request.query_params.get("company_name", None)
            self.company_symbol = request.query_params.get("company_symbol", None)
            if self.company_name and self.company_symbol:
                data = {"response_msg":"You can either pass company name or company symbol in the request, not both"}
                return Response(data, status=400)
            else:
                if len(request.query_params) != 3:
                    data = {"response_msg":"Please ensure all required params are passed in the request"}
                    return Response(data, status=400)
                else:
                    query_set = self.get_object()
                    print("Query set == ",query_set)
                    transaction = request.query_params.get("transc_type", None)
                    share_qty = int(request.query_params.get("share_qty", None))
                    total_share_price = query_set.share_price*share_qty
                    if transaction.lower() == 'buy':
                        if(share_qty>query_set.no_of_shares):
                            return Response(f"You can only buy {query_set.no_of_shares} or less shares", status=400)

                        current_user = request.user.id
                        user_data = UserClient.objects.get(user_id=current_user)
                        if(user_data.funds >= total_share_price):

                            try:
                                user_shares = UserSharesData.objects.get(username_id=user_data.id, company_symbol = query_set.company_symbol)
                                user_shares.shares_qty += share_qty
                                user_shares.save()
                            except UserSharesData.DoesNotExist:
                                user_shares = UserSharesData(username=user_data,company_name=query_set.company_name, company_symbol=query_set.company_symbol,shares_qty=share_qty)
                                user_shares.save()

                            user_data.funds = user_data.funds - total_share_price    
                            user_data.save()         
                            query_set.no_of_shares = query_set.no_of_shares-share_qty
                            query_set.last_updated_date = datetime.date.today()
                            query_set.save()
                            msg = "Shares bought and db updated"
                            data = {"response_msg":msg}
                            json_resp = json.dumps({"response_msg":msg})
                            return Response(data, status=200)
                        else:
                            data = {"response_msg":"You dont have enough funds in account"}
                            return Response(data, status=403)
                    
                    elif transaction.lower() == 'sell':

                        current_user = request.user.id
                        user_data = UserClient.objects.get(user_id=current_user)
                        try:
                                user_shares = UserSharesData.objects.get(username_id=user_data.id, company_symbol = query_set.company_symbol)
                                if(user_shares.shares_qty >= share_qty):
                                    user_shares.shares_qty -= share_qty
                                    user_shares.save()
                                    user_data.funds += (query_set.share_price * share_qty)
                                    user_data.save()
                                    query_set.no_of_shares = query_set.no_of_shares + share_qty
                                    query_set.last_updated_date = datetime.date.today()
                                    query_set.save()
                                    data = {"response_msg":"Shares sold and db updated"}
                                    return Response(data, status=200)
                                else:
                                    data = {"response_msg":f"You dont have {share_qty} shares in account to sell"}
                                    return Response(data, status=403)

                        except UserSharesData.DoesNotExist:
                            data = {"response_msg":f"You dont have share of {query_set.company_name} to sell"}
                            return Response(data,status=404)
                            # raise Http404(f"You dont have share of {query_set.company_name} to sell")

                        
        else:
            return HttpResponseRedirect(reverse('login-user'))
        
class CurrencyExchange():
    api_key = 'PFB3RSVTguWxltMbkxr4rAA2Czh8aTLTcAoDbQzs'
    online_api_error = False
    rate = 0.0

    def getRateFromOnlineApi(self, from_currency, to_currency):
        url_conv = f"https://api.freecurrencyapi.com/v1/latest?base_currency={from_currency}"
        headers = CaseInsensitiveDict()
        headers["apikey"] = self.api_key

        return self.rate, True, 400

        # resp = requests.get(url_conv, headers=headers)
        # if resp.status_code != 200:
        #     self.online_api_error = True
        #     return self.rate, self.online_api_error, resp.status_code
        # else:
        #     resp = requests.get(url_conv, headers=headers)
        #     json_data = resp.json()
        #     self.rate = json_data['data'][to_currency]
        #     print(f'GBP rate to INR = {self.rate}')
        #     return self.rate, self.online_api_error, resp.status_code
        
    def getRateFromSelfBuildApi(self, from_currency, to_currency):
        print("Inside self api func ++++++++++++++++++++++++++++++++++++++++++++++++++++")
        url_conv = "http://localhost:8089/CurConvRS/webresources/exchangeRate"
        url_endpoint = f"{url_conv}?fromCur={from_currency}&toCur={to_currency}"
        try:
            resp = requests.get(url_endpoint)

            resp.raise_for_status()
        except Exception as e:
            return self.rate, True, e
        else:
            self.online_api_error = False
            json_data = resp.json()
            self.rate = json_data['rate']
            return self.rate, False, ""
        

class findForeignRate(APIView):
    company_name = None
    company_symbol = None
    currency_ex_obj = CurrencyExchange()
    ex_rate = 0.0

    def get_object(self):
        try:
            if self.company_symbol:
                print(f'line no 310............... {self.company_symbol}')
                print(f'symbol ============ {self.company_symbol}')
                return SharesData.objects.get(company_symbol = self.company_symbol)
            elif self.company_name:
                print(f'line no 313............... {self.company_name}')
                return SharesData.objects.get(company_name=self.company_name)

        except SharesData.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.company_name = request.query_params.get("company_name", None)
            self.company_symbol = request.query_params.get("company_symbol", None)
            # if self.company_name and self.company_symbol:
            #     return Response("You can either pass company name or company symbol in the request, not both", status=400)
            to_currency = request.query_params.get("to_currency", None)
            if not to_currency:
                return Response("Target currency is required", status=400)
            else:
                to_currency =to_currency.upper()
                self.ex_rate, error_flag, status_code =  self.currency_ex_obj.getRateFromOnlineApi("GBP", to_currency)
                if error_flag:
                    self.ex_rate, error_flag2, error_msg = self.currency_ex_obj.getRateFromSelfBuildApi("GBP", to_currency)
                    if error_flag2:
                        return Response(f"Internal Error occured : {error_msg}", status=404)
                query_set = self.get_object()
                print("Query set == ",query_set)
                stock_rt_foreign_curr = query_set.share_price * self.ex_rate
                print(f"{query_set.company_name} price in {to_currency} = {stock_rt_foreign_curr}")
                serializer = SharesListSerializer(query_set)
                print(serializer.data)
                data = serializer.data
                data["exchange_currency"] = to_currency.upper()
                data["currency_rate"] = self.ex_rate
                data['currency_stock_price'] = stock_rt_foreign_curr
                return Response(data, status=200)

        else:
            return HttpResponseRedirect(reverse('login-user'))
        
class BuySellInForex(APIView):
    company_name = None
    company_symbol = None

    def get_object(self):
        try:
            if self.company_symbol:
                return SharesData.objects.get(company_symbol = self.company_symbol)
            elif self.company_name:
                return SharesData.objects.get(company_name=self.company_name)

        except SharesData.DoesNotExist:
            raise Http404
        
    def get_userForex_data(self, id, forex_currency):
        try:
            user_forex_data = UserCurrency.objects.get(username_id=id,currency_symbol=forex_currency)
            return user_forex_data
        except UserCurrency.DoesNotExist:
            return Response(f"You do not have funds in {forex_currency}, please add it first", status=406)
        
    
    def get(self, request):
        if request.user.is_authenticated:
            self.company_name = request.query_params.get("company_name", None)
            self.company_symbol = request.query_params.get("company_symbol", None)
            forex_rate = request.query_params.get("forex_rate", None)
            forex_currency = request.query_params.get("forex_currency", None)
            transaction = request.query_params.get("transc_type", None)
            share_qty = int(request.query_params.get("share_qty", None))

            query_set = self.get_object()
            current_user = request.user.id
            user_data = UserClient.objects.get(user_id=current_user)
            print("Query set == ",query_set)
            total_share_price = query_set.share_price*share_qty*float(forex_rate)
            if transaction.lower() == 'buy':
                if(share_qty>query_set.no_of_shares):
                    return Response(f"You can only buy {query_set.no_of_shares} or less shares", status=400)
                forex_data = self.get_userForex_data(user_data.id,forex_currency)
                if(forex_data.funds >= total_share_price):
                    try:
                        user_shares = UserSharesData.objects.get(username_id=user_data.id, company_symbol = query_set.company_symbol)
                        user_shares.shares_qty += share_qty
                        user_shares.save()
                    except UserSharesData.DoesNotExist:
                        user_shares = UserSharesData(username=user_data,company_name=query_set.company_name, company_symbol=query_set.company_symbol,shares_qty=share_qty)
                        user_shares.save()
                    forex_data.funds = forex_data.funds - total_share_price    
                    forex_data.save()         
                    query_set.no_of_shares = query_set.no_of_shares-share_qty
                    query_set.last_updated_date = datetime.date.today()
                    query_set.save()
                    return Response("Shares bought and db updated", status=200)
                else:
                    return Response("You dont have enough funds in account", status=403)
            
            elif transaction.lower() == 'sell':

                try:
                    forex_data = self.get_userForex_data(user_data.id,forex_currency)
                    user_shares = UserSharesData.objects.get(username_id=user_data.id, company_symbol = query_set.company_symbol)
                    if(user_shares.shares_qty >= share_qty):
                        user_shares.shares_qty -= share_qty
                        user_shares.save()
                        forex_data.funds += total_share_price
                        forex_data.save()
                        query_set.no_of_shares = query_set.no_of_shares + share_qty
                        query_set.last_updated_date = datetime.date.today()
                        query_set.save()
                        return Response("Shares sold and db updated", status=200)
                    else:
                        return Response(f"You dont have {share_qty} shares in account to sell", status=403)

                except UserSharesData.DoesNotExist:
                    return Response(f"You dont have share of {query_set.company_name} to sell",status=404)
        else:
            return HttpResponseRedirect(reverse('login-user'))
