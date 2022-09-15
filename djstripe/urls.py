from django.contrib import admin
from django.urls import path
from products.views import (CreateCheckoutSessionViewOrder,
                           CreateCheckoutSessionViewItem,
                           ProductLandingPageView,
                           ProductLandingPage,
                           
                           SuccessView,
                           CancelView,
                           OrderLandingPage
                           )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('card-item/<pk>/', ProductLandingPageView.as_view(), name='landing-page'),
    path('item/<pk>/', ProductLandingPage.as_view(), name='landing-page'),
    path('order/<pk>/', OrderLandingPage.as_view(), name='landing-page'),
    path('buy/<pk>/', CreateCheckoutSessionViewItem.as_view(), name='create-checkout-session'),
    path('buy-order/<pk>/', CreateCheckoutSessionViewOrder.as_view(), name='create-checkout-session'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
]
