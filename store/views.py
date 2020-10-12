from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
import stripe

from store.models import Item, Order, Tax, Discount
from stripe_store.settings import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY


class ItemDetail(View):
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
    template_name = 'store/checkout.html'

    def post(self, request):
        stripe.api_key = STRIPE_SECRET_KEY
        order = request.session.get('order_id', False)
        if order:
            total_price_change = toggle_taxes_and_discounts(order)
            order = Order.objects.filter(id=order).prefetch_related('items').annotate(
                total_price=Sum('items__price')
            ).get()
            amount = int(order.total_price + total_price_change) * 100
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
                'currency': 'rub'
            }
            return render(request, self.template_name, args)
        else:
            return HttpResponse('Корзина пуста')


def success_payment(request):
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


def cancel_payment(request):
    return render(request, 'store/cancel_payment.html')


def toggle_taxes_and_discounts(order):
    order = Order.objects.filter(id=order).prefetch_related('items', 'taxes', 'discounts').annotate(
        price=Sum('items__price'),
    ).get()

    order.taxes.clear()
    order.discounts.clear()

    taxes = Tax.objects.all()
    discounts = Discount.objects.all()

    total_price_change = 0

    order, price_change = check_conditions(order, taxes, 'taxes')
    total_price_change += price_change

    order, price_change = check_conditions(order, discounts, 'discounts')
    total_price_change += price_change

    order.save()
    return total_price_change


def check_conditions(order, queryset, query_type):
    price_change = 0
    for item in queryset:
        if item.order_price_condition == 'LTE':
            if order.price <= item.condition_price:
                if query_type == 'discounts':
                    price_change -= item.price
                    order.discounts.add(item)
                else:
                    price_change += item.price
                    order.taxes.add(item)

        elif item.order_price_condition == 'LT':
            if order.price < item.condition_price:
                if query_type == 'discounts':
                    price_change -= item.price
                    order.discounts.add(item)
                else:
                    price_change += item.price
                    order.taxes.add(item)

        elif item.order_price_condition == 'GT':
            if order.price > item.condition_price:
                if query_type == 'discounts':
                    price_change -= item.price
                    order.discounts.add(item)
                else:
                    price_change += item.price
                    order.taxes.add(item)

        elif item.order_price_condition == 'GTE':
            if order.price >= item.condition_price:
                if query_type == 'discounts':
                    price_change -= item.price
                    order.discounts.add(item)
                else:
                    price_change += item.price
                    order.taxes.add(item)

        elif item.order_price_condition == 'EQ':
            if order.price == item.condition_price:
                if query_type == 'discounts':
                    price_change -= item.price
                    order.discounts.add(item)
                else:
                    price_change += item.price
                    order.taxes.add(item)
    return order, price_change
