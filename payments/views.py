from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def subscribe_view(request):
    form = SubscribeForm(request, data=request.POST)
    return render(request, 'payments.html', {'form': form})