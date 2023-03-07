from rest_framework import serializers
from .models import SharesData

class SharesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharesData
        fields = ['company_name', 'company_symbol', 'no_of_shares', 'share_currency', 'share_price', 'last_updated_date']