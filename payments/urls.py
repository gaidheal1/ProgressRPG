from django.urls import path

#from . import views
from .views import ProductsView, AfterCheckoutView
#from .views import CreateCheckoutSession

urlpatterns = [
    path('subscription/', ProductsView.as_view(), name='products'),
    path('after-checkout/', AfterCheckoutView.as_view(), name='after-checkout'),
    #path('create-checkout-session/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    #path('checkout/', views.checkout, name='checkout'),
    #path('success/', views.success_view, name='success'),
    #path('cancel/', views.cancel_view, name='cancel'),
    #path('webhook/', views.webhook, name='webhook'),

]

