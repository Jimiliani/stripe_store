from django.db import models
from django.urls import reverse

LTE = 'LTE'
LT = 'LT'
GTE = 'GTE'
GT = 'GT'
EQ = 'EQ'
PRICE_CONDITION_CHOICES = [
    (LTE, '<='),
    (LT, '<'),
    (GTE, '>='),
    (GT, '>'),
    (EQ, '='),
]


class Item(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    price = models.PositiveIntegerField(null=False, blank=False)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('store:buy-item', args=[self.id])


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders')

    def __str__(self):
        return 'order ' + str(self.id)


class Tax(models.Model):
    DELIVERY = 'DV'
    ADDITIONAL_COST = 'AC'
    TAXES_CHOICES = [
        (DELIVERY, 'Доставка'),
        (ADDITIONAL_COST, 'НДС')
    ]
    orders = models.ManyToManyField(Order, related_name='taxes', null=True, blank=True)
    price = models.PositiveIntegerField()
    condition_price = models.PositiveIntegerField()
    keyword = models.CharField(max_length=3, choices=TAXES_CHOICES)
    order_price_condition = models.CharField(
        help_text='Условный оператор, который должен выполниться, для использования этого налога, например,'
                  ' если в этом поле указан знак ">", то если "цена заказа" > "цена налога", то налог активируется'
                  ' относительно данного заказа', max_length=3, choices=PRICE_CONDITION_CHOICES)

    def __str__(self):
        return self.keyword + ' ' + str(self.price)


class Discount(models.Model):
    FREE_DELIVERY = 'FDV'
    BIG_ORDER = 'BO'
    DISCOUNT_CHOICES = [
        (FREE_DELIVERY, 'Бесплатная доставка'),
        (BIG_ORDER, 'Большой заказ')
    ]
    orders = models.ManyToManyField(Order, related_name='discounts', null=True, blank=True)
    price = models.PositiveIntegerField()
    condition_price = models.PositiveIntegerField()
    keyword = models.CharField(max_length=3, choices=DISCOUNT_CHOICES)
    order_price_condition = models.CharField(
        help_text='Условный оператор, который должен выполниться, для использования этой скидки, например,'
                  ' если в этом поле указан знак ">", то если "цена заказа" > "цена скидки", то скидка активируется'
                  ' относительно данного заказа', max_length=3, choices=PRICE_CONDITION_CHOICES)

    def __str__(self):
        return self.keyword + ' ' + str(self.price)
