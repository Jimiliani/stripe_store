from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
import stripe

from store.models import Item, Order
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
        # request.session.flush()
        stripe.api_key = STRIPE_SECRET_KEY
        order = request.session.get('order_id', False)
        if order:
            order = Order.objects.filter(id=order).prefetch_related('items').annotate(
                total_price=Sum('items__price')
            ).values()[0]
            if 'payment_intent_id' not in request.session:
                intent = stripe.PaymentIntent.create(
                    amount=int(order['total_price']) * 100,
                    currency='rub',
                    payment_method_types=['card']
                )
                request.session['payment_intent_id'] = intent.id
            else:
                intent = stripe.PaymentIntent.modify(
                    request.session['payment_intent_id'],
                    amount=int(order['total_price']) * 100,
                )
            args = {
                'secret_key': intent.client_secret,
                'pub_key': STRIPE_PUBLISHABLE_KEY,
                'payment_intent_id': intent.id
            }
            return render(request, self.template_name, args)
        else:
            return HttpResponse('Корзина пуста')
        # return HttpResponse('asd')


def success_payment(request):
    return render(request, 'store/success_payment.html')


def cancel_payment(request):
    return render(request, 'store/cancel_payment.html')
