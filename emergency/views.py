from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import EmergencyAlert
from .data import districts, EMERGENCY_NUMBERS

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

@login_required
def emergency_menu(request):
    """
    Show the Emergency Menu page for logged-in users.
    """
    return render(request, 'emergency/menu.html')


@login_required
def emergency_dashboard(request):
    # Here you can pass any data you want to show on the emergency page
    return render(request, 'emergency/emergency.html')


@login_required
def get_emergency_contacts(request):
    """
    API endpoint to get emergency contacts based on location or district
    """
    district = request.GET.get('district', 'Kathmandu')
    emergency_type = request.GET.get('type', 'hospital')
    
    # Get district data
    district_data = districts.get(district, districts['Kathmandu'])
    
    response_data = {
        'district': district,
        'emergency_type': emergency_type,
        'contacts': []
    }
    
    if emergency_type == 'hospital':
        response_data['contacts'] = district_data.get('hospitals', [])
    elif emergency_type == 'police':
        police_numbers = district_data.get('police', [])
        response_data['contacts'] = [
            {'name': 'District Police', 'phone': phone, 'type': 'police'} 
            for phone in police_numbers
        ]
    
    # Add universal emergency numbers
    universal_contacts = [
        {'name': 'Universal Emergency', 'phone': EMERGENCY_NUMBERS['universal_emergency'], 'type': 'universal'},
        {'name': 'Police', 'phone': EMERGENCY_NUMBERS['police'], 'type': 'police'},
        {'name': 'Fire Brigade', 'phone': EMERGENCY_NUMBERS['fire_brigade'], 'type': 'fire'},
        {'name': 'Ambulance', 'phone': EMERGENCY_NUMBERS['ambulance'], 'type': 'ambulance'},
        {'name': 'Tourist Police', 'phone': EMERGENCY_NUMBERS['tourist_police'], 'type': 'tourist_police'},
    ]
    
    response_data['universal_contacts'] = universal_contacts
    
    return JsonResponse(response_data)


@login_required
def nearby_hospitals(request):
    """
    Show nearby hospitals and medical emergency information
    """
    context = {
        'districts': districts,
        'emergency_numbers': EMERGENCY_NUMBERS
    }
    return render(request, 'emergency/hospitals.html', context)


@login_required
def hospitals_api(request):
    """
    API endpoint to get hospitals data
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    district = request.GET.get('district')
    
    if district and district in districts:
        # Return hospitals for specific district
        district_data = districts[district]
        hospitals = district_data.get('hospitals', [])
        for hospital in hospitals:
            hospital['district'] = district
        return JsonResponse({'hospitals': hospitals, 'district': district})
    
    # Return all hospitals if no specific district
    all_hospitals = []
    for district_name, district_data in districts.items():
        hospitals = district_data.get('hospitals', [])
        for hospital in hospitals:
            hospital['district'] = district_name
            all_hospitals.append(hospital)
    
    # Sort by some criteria (in real app, by distance)
    all_hospitals = all_hospitals[:20]  # Limit to 20 nearest
    
    return JsonResponse({'hospitals': all_hospitals})


@login_required
def emergency_contacts(request):
    """
    Emergency contacts management page
    """
    return render(request, 'emergency/contacts.html')


@login_required  
def emergency_map(request):
    """
    Show emergency services on a map
    """
    context = {
        'districts': districts,
        'emergency_numbers': EMERGENCY_NUMBERS
    }
    return render(request, 'emergency/map.html', context)


