from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.IntegerField(default=0) # in pennies
    interval = models.CharField(max_length=10, choices=[
        ('month1', 'Monthly'), 
        ('month3', '3 Months'), 
        ('month6', '6 Months'), 
        ('yearly', 'Yearly')
    ])
    stripe_plan_id = models.CharField(max_length=100) # ID from Stripe dashboard

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)


class StripeCheckoutSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)