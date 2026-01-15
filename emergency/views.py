from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import EmergencyAlert

@login_required
def sos_alert(request):
    if request.method == "POST":
        alert = EmergencyAlert.objects.create(
            user=request.user,
            booking_id=request.POST.get('booking_id'),
            emergency_type=request.POST['emergency_type'],
            severity=request.POST['severity'],
            location=request.POST['location'],
            message=request.POST.get('message', ''),
            symptoms=request.POST.get('symptoms', ''),
        )
        return redirect('emergency_status', alert.id)

    return render(request, 'emergency/sos.html')


@login_required
def emergency_status(request, id):
    alert = get_object_or_404(EmergencyAlert, id=id, user=request.user)
    return render(request, 'emergency/status.html', {'alert': alert})


@login_required
def emergency_history(request):
    alerts = EmergencyAlert.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'emergency/history.html', {'alerts': alerts})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def emergency_menu(request):
    """
    Show the Emergency Menu page for logged-in users.
    """
    return render(request, 'emergency/menu.html')


# emergency/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def emergency_dashboard(request):
    # Here you can pass any data you want to show on the emergency page
    return render(request, 'emergency/emergency.html')


