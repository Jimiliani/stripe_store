from django.urls import path

from .views import ItemDetail, BuyItem, PayForGoods, success_payment

app_name = 'store'

urlpatterns = [
    path('item/<int:pk>', ItemDetail.as_view(), name='item-detail'),
    path('buy/<int:pk>', BuyItem.as_view(), name='buy-item'),
    path('pay_for_goods', PayForGoods.as_view(), name='pay-for-goods'),
    path('success_payment', success_payment, name='success-payment'),
]
