from rest_framework import serializers
from .models import UserCurrency,UserSharesData

class UserCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCurrency
        fields = '__all__'

class UserStocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSharesData
        fields = '__all__'