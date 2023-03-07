from django.urls import path
from .views import ShareList, ShareChangePrice, ShareUpdatQty, BuySellShares

urlpatterns = [
    path('listShares', ShareList.as_view(), name="list-of-all-shares"),
    path('priceChange', ShareChangePrice.as_view(), name="change-share-price"),
    path('quantityUpdate', ShareUpdatQty.as_view(), name="update-share-quantity"),
    path('shareTransc', BuySellShares.as_view(), name="buy-sell-share"),

]