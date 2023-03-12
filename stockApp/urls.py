from django.urls import path
from .views import BuySellInForex, ShareList, ShareChangePrice, ShareUpdatQty, BuySellShares, findForeignRate, stockDetail

urlpatterns = [
    path('detail/<str:company_symbol>', stockDetail, name="detail-page"),
    path('listShares', ShareList.as_view(), name="list-of-all-shares"),
    path('priceChange', ShareChangePrice.as_view(), name="change-share-price"),
    path('quantityUpdate', ShareUpdatQty.as_view(), name="update-share-quantity"),
    path('shareTransc', BuySellShares.as_view(), name="buy-sell-share"),
    path('findForeignRate', findForeignRate.as_view(), name="find-foreign-rate"),
    path('buySellForCur', BuySellInForex.as_view(), name="buy-sell-stock-forex"),

]