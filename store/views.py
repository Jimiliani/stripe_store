from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
import stripe

from store.models import Item, Order, Tax, Discount
from stripe_store.settings import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY


class ItemDetail(View):
    """

    Отображает информацию о товаре

    """
    template_name = 'store/item_detail.html'

    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        is_item_in_order = False
        order = request.session.get('order_id', False)
        if order:
            is_item_in_order = Order.objects.filter(id=order, items=item).exists()
        args = {'item': item,
                'pub_key': STRIPE_PUBLISHABLE_KEY,
                'is_item_in_order': is_item_in_order}
        return render(request, self.template_name, args)


class BuyItem(View):
    """

    Добавляет/удаляет товар из текущего заказа пользователя

    """

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        if request.session.get('order_id', False):
            order = Order.objects.get(id=request.session['order_id'])
        else:
            order = Order.objects.create()
            request.session['order_id'] = order.id
        order.items.add(item)
        return HttpResponse()

    def delete(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        order = Order.objects.get(id=request.session['order_id'])
        order.items.remove(item)
        return HttpResponse()


class PayForGoods(View):
    """

    Осуществляется оплата заказа с учетом всех скидок и налогов

    """
    template_name = 'store/checkout.html'

    def post(self, request):
        stripe.api_key = STRIPE_SECRET_KEY
        order = request.session.get('order_id', False)
        if order:
            order = Order.objects.filter(id=order).annotate(
                total_price=Sum('items__price'),
            ).get()
            total_price_change, total_percentage_price_change = toggle_taxes_and_discounts(order)
            amount = int(order.total_price + total_price_change +
                         (order.total_price * total_percentage_price_change) / 100) * 100
            if 'payment_intent_id' not in request.session:
                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='rub',
                    payment_method_types=['card']
                )
                request.session['payment_intent_id'] = intent.id
            else:
                intent = stripe.PaymentIntent.modify(
                    request.session['payment_intent_id'],
                    amount=amount,
                )
            args = {
                'secret_key': intent.client_secret,
                'pub_key': STRIPE_PUBLISHABLE_KEY,
                'payment_intent_id': intent.id,
                'amount': int(amount / 100),
                'currency': '₽'
            }
            return render(request, self.template_name, args)
        else:
            return HttpResponse('Корзина пуста')


def success_payment(request):
    """

    Подтверждается оплата товара и показывается страница с сообщением об успехе операции
    :param request: обычный post запрос(в случае get запроса будет произведен redirect на страницу первого товара)
    :return: страница с сообщением об успешной покупке
    """
    if request.method == 'POST':
        payment_intent_id = request.POST['payment_intent_id']
        payment_method_id = request.POST['payment_method_id']

        stripe.api_key = STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            payment_intent_id,
            payment_method=payment_method_id
        )
        stripe.PaymentIntent.confirm(payment_intent_id)

        order = Order.objects.get(id=request.session.get('order_id', False))
        order.delete()
        request.session.flush()
        return render(request, 'store/success_payment.html')
    else:
        return redirect('store:item-detail', pk=1)


def toggle_taxes_and_discounts(order):
    """

    Добавляет к выбранному заказу все скидки и налоги условиям которых он удовлетворяет

    :param order: выбранный заказ
    :return: изменение цены в текущей валюте и изменение цены в процентах от нее
    """
    # удаляем все уже имеющиеся скидки и налоги
    order.taxes.clear()
    order.discounts.clear()
    # берем все существующие скидки и налоги
    taxes = Tax.objects.all()
    discounts = Discount.objects.all()

    total_price_change = 0
    total_percentage_price_change = 0
    # подсчитываем изменение цены из-за налогов
    order, price_change, percentage_price_change = check_conditions(order, taxes, 'taxes')
    total_price_change += price_change
    total_percentage_price_change += percentage_price_change
    # подсчитываем изменение цены из-за скидов
    order, price_change, percentage_price_change = check_conditions(order, discounts, 'discounts')
    total_price_change += price_change
    total_percentage_price_change += percentage_price_change
    # сохраняем имеющийся заказ с добавленными скидками, налогами и изменениями цены
    order.save()
    return total_price_change, total_percentage_price_change


def check_conditions(order, queryset, query_type):
    """

    Подсчитываем изменение цены заказа для данного order и всех налогов/скидок в queryset
    :param order: текущий заказ пользователя
    :param queryset: queryset скидок или налогов
    :param query_type: "discount" или "tax" в зависимости от того скидка это или налог
    :return: текущий заказ, изменение цены в единицах текущей валюты, изменение цены в процентах от нее
    """
    price_change = 0
    percentage_price_change = 0
    for item in queryset:
        if item.order_price_condition == 'LTE':
            if order.total_price <= item.condition_price:
                if item.percentage_price:
                    percentage_price_change = change_price(query_type, percentage_price_change, item, order)
                else:
                    price_change = change_price(query_type, price_change, item, order)

        elif item.order_price_condition == 'LT':
            if order.total_price < item.condition_price:
                if item.percentage_price:
                    percentage_price_change = change_price(query_type, percentage_price_change, item, order)
                else:
                    price_change = change_price(query_type, price_change, item, order)

        elif item.order_price_condition == 'GT':
            if order.total_price > item.condition_price:
                if item.percentage_price:
                    percentage_price_change = change_price(query_type, percentage_price_change, item, order)
                else:
                    price_change = change_price(query_type, price_change, item, order)

        elif item.order_price_condition == 'GTE':
            if order.total_price >= item.condition_price:
                if item.percentage_price:
                    percentage_price_change = change_price(query_type, percentage_price_change, item, order)
                else:
                    price_change = change_price(query_type, price_change, item, order)

        elif item.order_price_condition == 'EQ':
            if order.total_price == item.condition_price:
                if item.percentage_price:
                    percentage_price_change = change_price(query_type, percentage_price_change, item, order)
                else:
                    price_change = change_price(query_type, price_change, item, order)
    return order, price_change, percentage_price_change


def change_price(query_type, price_change, item, order):
    """

    Непосредственно производим расчеты для данного налога/скидки

    :param query_type: "discount" или "tax" в зависимости от того скидка это или налог
    :param price_change: измеющееся на данный момент изменение цены
    :param item: текущий налог или скидка
    :param order: текущий заказ
    :return: новое изменение цены
    """
    if query_type == 'discounts':
        price_change -= item.price
        order.discounts.add(item)
    else:
        price_change += item.price
        order.taxes.add(item)
    return price_change
