from django.contrib import admin

# Register your models here.

from .models import SubscriptionPlan, UserSubscription, StripeCheckoutSession

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'interval', 'stripe_plan_id')
    #search_fields = ('name',)
    #list_filter = ('interval',)
    #ordering = ('name',)


#@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'active')
    fields = [
        'user',
        'plan',
        'stripe_subscription_id',
        'active',
        'start_date',
        'end_date',
    ]
    #search_fields = ('user__username', 'plan__name')
    #list_filter = ('active',)
    #ordering = ('-start_date',)
    
#@admin.register(StripeCheckoutSession)
class StripeCheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'fulfilled', 'created_at')
    #search_fields = ('session_id',)
    #list_filter = ('fulfilled',)
    #ordering = ('-created_at',)