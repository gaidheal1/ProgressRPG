from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from django.http import JsonResponse
from .models import SubscriptionPlan


# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request, plan_id):
    plan = SubscriptionPlan.objects.get(id=plan_id)

    # Create Stripe checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price': plan.stripe_plan_id, # Use the Stripe price ID
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url=request.build_absolute_uri('/subscriptions/success/'),
        cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
    )
    
    return JsonResponse({'id': checkout_session.id})

@login_required
def subscribe_view(request):
    user = request.user
    if request.method =='POST':
        user.profile.onboarding_step = 4
        user.profile.save()
        return redirect('game')
    return render(request, 'payments/subscribe.html')