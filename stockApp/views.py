import datetime
import os
from enum import Enum


from django.core.exceptions import BadRequest
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from userClients.models import UserClient, UserSharesData
from .models import SharesData
from .serializers import SharesListSerializer


class ModelFilterFields(Enum):
    COMPANY_NAME = "company_name"
    COMPANY_SYMBOL = "company_symbol"

def apiOverView(request):
    return JsonResponse("API demo", safe=False)

class ShareList(APIView):
    company_name = None
    company_symbol = None
    max_share_price = False
    max_quantity = False


    def get_queryset(self):
        queryset = SharesData.objects.all()
        self.company_name = self.request.query_params.get("company_name", None)
        self.company_symbol = self.request.query_params.get("company_symbol", None)
        self.max_share_price = self.request.query_params.get("max_share_price", False)
        self.max_quantity = self.request.query_params.get("max_quantity", False)
        self.min_share_price = self.request.query_params.get("min_share_price", False)
        self.min_quantity = self.request.query_params.get("min_quantity", False)



        if self.company_name:
            queryset = queryset.filter(company_name=self.company_name)
            return queryset
        elif self.company_symbol:
            queryset = queryset.filter(company_symbol=self.company_symbol)
            return queryset
        elif self.max_share_price:
            queryset = queryset.order_by('-share_price')[:1]
            return queryset
        elif self.max_quantity:
            queryset = queryset.order_by('-no_of_shares')[:1]
            return queryset
        elif self.min_share_price:
            queryset = queryset.order_by('share_price')[:1]
            return queryset
        elif self.min_quantity:
            queryset = queryset.order_by('no_of_shares')[:1]
            return queryset
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
                return Response("You can either pass company name or company symbol in the request, not both", status=400)
            else:
                if len(request.query_params) != 3:
                    return Response("Please ensure all required params are passed in the request", status=400)
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
                            return Response("Shares bought and db updated", status=200)
                        else:
                            return Response("You dont have enough funds in account", status=403)
                    
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
                                    return Response("Shares sold and db updated", status=200)
                                else:
                                    return Response(f"You dont have {share_qty} shares in account to sell", status=403)

                        except UserSharesData.DoesNotExist:
                            return Response(f"You dont have share of {query_set.company_name} to sell",status=404)
                            # raise Http404(f"You dont have share of {query_set.company_name} to sell")

                        
        else:
            return HttpResponseRedirect(reverse('login-user'))