from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import stripe, logging, traceback

#from .models import SubscriptionPlan
from .utils import confirm_checkout, fulfill_checkout

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger("django")


class ProductsView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/products.html'

    def get(self, request, *args, **kwargs):
        # Fetch subscription plans from the database or any other source
        # For example:
        # self.subscription_plans = SubscriptionPlan.objects.all()
        context = self.get_context_data(user=request.user)
        return self.render_to_response(context)
        #return super().get(request, *args, **kwargs)


class AfterCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/after_checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if not session_id:
            logger.warning("[AFTER CHECKOUT] No session ID provided in the request.")
            return render(request, 'payments/after_checkout_error.html', {
                'message': 'No session ID provided.'
            })
        checkout_session = None
        try:
            logger.debug(f"[AFTER CHECKOUT] Attempting to confirm checkout session: {session_id}")
            checkout_session = confirm_checkout(session_id)

            if checkout_session:
                logger.debug(f"Checkout session {checkout_session.id} confirmed. Proceeding to fulfillment.")
                success = fulfill_checkout(checkout_session)
                if not success:
                    logger.error(f"[AFTER CHECKOUT] Fulfillment failed for checkout session {checkout_session.id}.")
                    raise RuntimeError(f"Checkout session {checkout_session.id} was confirmed but fulfillment failed.")

                logger.debug(f"[AFTER CHECKOUT] Fulfillment succeeded for checkout session {checkout_session.id}. Rendering response.")
                context = self.get_context_data(checkout_session=checkout_session)
                return self.render_to_response(context)
            
            else:
                logger.warning(f"[AFTER CHECKOUT] Checkout session {session_id} not found or already fulfilled.")
                return render(request, 'payments/after_checkout_error.html', {
                    'message': 'Something went wrong confirming your payment.'
                })
            
        except Exception as e:
            logger.error(f"[AFTER CHECKOUT] Unexpected error while handling checkout session {session_id}: {e}\n{traceback.format_exc()}")
            return render(request, 'payments/after_checkout_error.html', {
                "message": "Please contact support if the problem continues."
            })


#@login_required
class CreateCheckoutSession(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, price_1234) of the product you want to sell
                        'price': 'price_1RD64HGHaENuGVuPj5B5HdSz',
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return redirect(checkout_session.url, code=303)








def success_view(request):
    # You can render a template or return a simple message
    return render(request, 'success.html')

def cancel_view(request):
    return render(request, 'cancel.html')





# Use the secret provided by Stripe CLI for local testing
# or your webhook endpoint's secret.
endpoint_secret = 'whsec_...'

@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
    fulfill_checkout(event['data']['object']['id'])

  return HttpResponse(status=200)










#@login_required
def subscribe_view(request):
    user = request.user
    if request.method =='POST':
        user.profile.onboarding_step = 4
        user.profile.save()
        return redirect('game')
    return render(request, 'payments/subscribe.html')