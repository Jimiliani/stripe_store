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
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name='Название')
    description = models.TextField(null=False, blank=True, verbose_name='Описание')
    price = models.PositiveIntegerField(null=False, blank=False, verbose_name='Цена')

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('store:buy-item', args=[self.id])

    class Meta:
        verbose_name = 'Вещь'
        verbose_name_plural = 'Вещи'


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders', verbose_name='Вещи')

    def __str__(self):
        return 'order ' + str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Tax(models.Model):
    DELIVERY = 'DV'
    ADDITIONAL_COST = 'AC'
    TAXES_CHOICES = [
        (DELIVERY, 'Доставка'),
        (ADDITIONAL_COST, 'НДС')
    ]
    orders = models.ManyToManyField(Order, related_name='taxes', blank=True, verbose_name='Заказы')
    price = models.PositiveIntegerField(verbose_name='Цена')
    percentage_price = models.BooleanField(default=False, verbose_name='Цена налога указана в процентах')
    condition_price = models.PositiveIntegerField(verbose_name='Цена для условия')
    keyword = models.CharField(max_length=3, choices=TAXES_CHOICES, verbose_name='Вид налога')
    order_price_condition = models.CharField(
        verbose_name='Оператор условия',
        help_text='Условный оператор, который должен выполниться, для использования этого налога, например,'
                  ' если в этом поле указан знак ">", то если "цена заказа" > "цена налога", то налог активируется'
                  ' относительно данного заказа', max_length=3,
        choices=PRICE_CONDITION_CHOICES)

    def __str__(self):
        return self.keyword + ' ' + str(self.price)

    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'


class Discount(models.Model):
    MIDDLE_ORDER = 'MO'
    BIG_ORDER = 'BO'
    DISCOUNT_CHOICES = [
        (MIDDLE_ORDER, 'Средний заказ'),
        (BIG_ORDER, 'Большой заказ')
    ]
    orders = models.ManyToManyField(Order, related_name='discounts', blank=True, verbose_name='Заказы')
    price = models.PositiveIntegerField(verbose_name='Цена')
    percentage_price = models.BooleanField(default=False, verbose_name='Цена скидки указана в процентах')
    condition_price = models.PositiveIntegerField(verbose_name='Цена для условия')
    keyword = models.CharField(max_length=3, choices=DISCOUNT_CHOICES, verbose_name='Вид налога')
    order_price_condition = models.CharField(
        verbose_name='Оператора условия',
        help_text='Условный оператор, который должен выполниться, для использования этой скидки, например,'
                  ' если в этом поле указан знак ">", то если "цена заказа" > "цена скидки", то скидка активируется'
                  ' относительно данного заказа', max_length=3, choices=PRICE_CONDITION_CHOICES)

    def __str__(self):
        return self.keyword + ' ' + str(self.price)

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
