from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
import stripe, logging, datetime

from .models import StripeCheckoutSession, UserSubscription, SubscriptionPlan


# Set your secret key. Remember to switch to your live secret key in production.
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger("django")




@transaction.atomic
def confirm_checkout(session_id):
    logger.info(f"Confirming Checkout Session id {session_id}")

    # Step 1: Check if fulfillment already exists
    try:
        fulfillment_record = StripeCheckoutSession.objects.select_for_update().get(
            session_id=session_id,
            fulfilled=False
        )
        if fulfillment_record.fulfilled:
            logger.warning("Checkout already fulfilled.")
            return None
    except StripeCheckoutSession.DoesNotExist:
        fulfillment_record = StripeCheckoutSession.objects.create(session_id=session_id, fulfilled=False)
        logger.debug(f"[CONFIRM CHECKOUT] StripeCheckoutSession object created")

    # Step 2: Retrieve session from Stripe
    logger.debug(f"[CONFIRM CHECKOUT] Retreiving Stripe checkout session.")
    checkout_session = None
    try:
        checkout_session = stripe.checkout.Session.retrieve(
        session_id,
        expand=['line_items', 'customer', 'subscription'],
    )
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        # logger.error('Status is: %s' % e.http_status)
        # logger.error('Code is: %s' % e.code)
        # param is '' in this case
        # logger.error('Param is: %s' % e.param)
        # logger.error('Message is: %s' % e.user_message)
        logger.error(f"[CONFIRM CHECKOUT] Card Error: {e}")
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        logger.error(f"[CONFIRM CHECKOUT] Rate Limit Error: {e}")
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        logger.error(f"[CONFIRM CHECKOUT] Invalid Request Error: {e}")
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        logger.error(f"[CONFIRM CHECKOUT] Authentication Error: {e}")
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        logger.error(f"[CONFIRM CHECKOUT] API Connection Error: {e}")
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        logger.error(f"[CONFIRM CHECKOUT] Stripe Error: {e}")
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        logger.error(f"[CONFIRM CHECKOUT] Unexpected Error: {e}")
    return checkout_session



def fulfill_checkout(checkout_session):
    logger.info(f"[FULFILL CHECKOUT] Checkout Session id {checkout_session.id}")
    #logger.debug(f"Checkout Session details: {checkout_session}")
    
    if checkout_session.payment_status != 'paid':
        logger.warning("Payment not completed.")
        return False
    
    email = checkout_session.customer_details.email
    User = get_user_model()
    try:
        user = User.objects.filter(email=email).first()
    except User.DoesNotExist:
        logger.error(f"User with email {email} does not exist.")
        return False

    logger.debug(f"User stripe customer id: {user.stripe_customer_id}, Stripe customer id: {checkout_session.customer.id}")
    if user and not user.stripe_customer_id:
        user.stripe_customer_id = checkout_session.customer.id
        user.save()

    for item in checkout_session.line_items.data:
        # Example: Upgrade user account, send email, etc.
        logger.debug(f"Fulfilling item: {item}")
        
        logger.debug(f"Item price id: {item.price.id}")

        plan=SubscriptionPlan.objects.get("price_1RDTXUGHaENuGVuPegMpIIxq"),
        logger.debug(f"Plan: {plan}")
        logger.debug(f"Start and end: {item.current_period_start}, {datetime.fromtimestamp(item.current_period_end)}")

        logger.debug(f"checkout_session.subscription.id: {checkout_session.subscription.id}")
        
        UserSubscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=checkout_session.subscription.id if checkout_session.subscription else None,
            active=True,
            start_date=datetime.fromtimestamp(item.current_period_start),
            end_date=datetime.fromtimestamp(item.current_period_end) if item.current_period_end else None,
        )

    fulfillment_record = StripeCheckoutSession.objects.get(session_id=checkout_session.id)
    fulfillment_record.fulfilled = True
    fulfillment_record.save()

    return True


