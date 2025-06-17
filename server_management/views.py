from django.shortcuts import render

def maintenance_view(request):
    profile = request.user.profile
    
    return render(request, 'server_management/maintenance.html', {"profile": profile})
    