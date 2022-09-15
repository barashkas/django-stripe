import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from products.models import Item, Order
import re

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class OrderLandingPage(View):
    def get(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({
                'error': "DoesNotExist"
                })
        if len(order.products.split(','))!=len(order.quantity.split(',')):
            return JsonResponse({
                'error': "OrderSizeError"
                })
        if len(order.products) == 0:
            return JsonResponse({
                'error': "OrderEmpty"
                })
        if len(order.quantity) == 0:
            return JsonResponse({
                'error': "OrdersQuantityEmpty"
                })
        products_list = re.sub('[^,^0-9]', '', order.products).split(',')
        quantity_list = re.sub('[^,^0-9]', '', order.quantity).split(',')
        res = []
        errors = []
        total_cost = 0
        for k, i in enumerate(products_list):
            try:
                product = Item.objects.get(id=int(i))
                quantity = int(quantity_list[k])
                items_cost = product.price*quantity
                res.append({
                        'item_id': i,
                        'item_name': product.name,
                        'item_price': product.price,
                        'quantity': quantity,
                        'items_cost': items_cost
                        })   
                total_cost += items_cost
            except Item.DoesNotExist:
                errors.append({
                        'item_id': i,
                        'error': 'DoesNotExist'                         
                        })
        if len(errors) == 0:
            return JsonResponse({
                'orders': res,
                'total_cost': total_cost
                })
        else:
            return JsonResponse({
                'orders': res,
                'errors': errors,
                'total_cost': total_cost
                })


class ProductLandingPage(View):
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        try:
            product = Item.objects.get(id=product_id)
        except Item.DoesNotExist:
            return JsonResponse({
                'error': "DoesNotExist"
                })
        return JsonResponse({
                'name': product.name,
                'description': product.description,
                'price': product.price
                })


class ProductLandingPageView(TemplateView):
    template_name = 'landing.html'
    
    def get_context_data(self, **kwargs):
        product_id = self.kwargs["pk"]
        try:
            product = Item.objects.get(id=product_id)
        except Item.DoesNotExist:
            product = None
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


class CreateCheckoutSessionViewOrder(View):
    def get(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            order = None
            return JsonResponse({
                'error': "DoesNotExist"
                })
        if len(order.products.split(','))!=len(order.quantity.split(',')):
            return JsonResponse({
                'error': "OrderSizeError"
                })
        if len(order.products) == 0:
            return JsonResponse({
                'error': "OrderEmpty"
                })
        if len(order.quantity) == 0:
            return JsonResponse({
                'error': "OrdersQuantityEmpty"
                })
        
        products_list = re.sub('[^,^0-9]', '', order.products).split(',')
        quantity_list = re.sub('[^,^0-9]', '', order.quantity).split(',')
        order_description = 'Order detalization:' 
                            
        total_cost = 0
        for k, i in enumerate(products_list):
            try:
                product = Item.objects.get(id=int(i))
                quantity = int(quantity_list[k])
                items_cost = product.price*quantity
                price_2f = "{0:.2f}".format(product.price / 100)
                cost_2f = "{0:.2f}".format(items_cost / 100)
                order_description +='{0} ({1}) [{2} * ${3} = ${4}]'.format(
                        product.name, i, quantity, price_2f, cost_2f)
                total_cost += items_cost
            except Item.DoesNotExist:
                continue  
    
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {      
                    'price_data': {
                            'currency': 'usd',
                            'unit_amount': total_cost,
                            'product_data': {
                                'name': 'Order {0}'.format(order_id),
                                'description': order_description,
                                },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
    
        return redirect(checkout_session.url, code=303)
        #return JsonResponse({
        #        'id': checkout_session.id
        #})


class CreateCheckoutSessionViewItem(View):
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        try:
            product = Item.objects.get(id=product_id)
        except Item.DoesNotExist:
            product = None
            return JsonResponse({
                'error': "DoesNotExist"
                })
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {      
                    'price_data': {
                            'currency': 'usd',
                            'unit_amount': product.price,
                            'product_data': {
                                'name': product.name,
                                'description': product.description,
                                },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url, code=303)
        #return JsonResponse({
        #        'id': checkout_session.id
        #})
    
    
