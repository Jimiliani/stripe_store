from django.contrib import admin
from django.contrib.auth.models import User, Group

from store.models import Item, Order, Tax, Discount


class M2MModelAdmin(admin.ModelAdmin):
    """

    Кастомизация панели заказов

    """
    filter_horizontal = ['orders', ]


class OrderAdmin(admin.ModelAdmin):
    """

    Кастомизация панели заказов


    """
    filter_horizontal = ['items', ]


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(Tax, M2MModelAdmin)
admin.site.register(Discount, M2MModelAdmin)
