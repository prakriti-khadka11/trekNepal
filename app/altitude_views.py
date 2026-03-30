from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    AltitudeProfile, AcclimatizationPlan, SymptomLog, EmergencyProtocol
)
import json

@login_required
def altitude_dashboard(request):
    """Main altitude sickness prevention dashboard"""
    try:
        altitude_profile = AltitudeProfile.objects.get(user=request.user)
    except AltitudeProfile.DoesNotExist:
        altitude_profile = None

    active_plans = AcclimatizationPlan.objects.filter(user=request.user, is_active=True)
    recent_logs = SymptomLog.objects.filter(user=request.user).order_by('-date')[:7]
    latest_log = recent_logs.first() if recent_logs else None
    prev_log = list(recent_logs)[1] if len(list(recent_logs)) > 1 else None

    # Day-over-day AMS change
    ams_change = None
    if latest_log and prev_log:
        ams_change = latest_log.get_ams_score() - prev_log.get_ams_score()

    # Altitude gain warning
    alt_gain = None
    if latest_log and prev_log:
        alt_gain = latest_log.current_altitude - prev_log.current_altitude

    # Chart data for inline trend (last 7 logs, chronological)
    import json
    chart_logs = list(reversed(list(recent_logs)))
    chart_data = json.dumps([{
        'date': str(l.date),
        'ams': l.get_ams_score(),
        'alt': l.current_altitude,
        'spo2': l.oxygen_saturation or None,
    } for l in chart_logs])

    context = {
        'altitude_profile': altitude_profile,
        'active_plans': active_plans,
        'recent_logs': recent_logs,
        'latest_log': latest_log,
        'prev_log': prev_log,
        'ams_change': ams_change,
        'alt_gain': alt_gain,
        'chart_data': chart_data,
        'has_profile': altitude_profile is not None,
        'symptom_fields': [
            ('headache',         'Headache'),
            ('nausea',           'Nausea'),
            ('fatigue',          'Fatigue'),
            ('dizziness',        'Dizziness'),
            ('sleep_difficulty', 'Sleep Difficulty'),
            ('appetite_loss',    'Appetite Loss'),
        ],
        'sym_choices': [(0,'None'),(1,'Mild'),(2,'Mod'),(3,'Severe')],
    }
    return render(request, 'altitude/dashboard.html', context)

@login_required
def create_altitude_profile(request):
    """Create or update user's altitude profile"""
    try:
        profile = AltitudeProfile.objects.get(user=request.user)
    except AltitudeProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        try:
            if profile:
                # Update existing profile
                profile.age = request.POST.get('age')
                profile.fitness_level = request.POST.get('fitness_level')
                profile.previous_altitude_experience = request.POST.get('previous_altitude_experience') == 'on'
                profile.max_altitude_reached = request.POST.get('max_altitude_reached', 0)
                profile.has_altitude_sickness_history = request.POST.get('has_altitude_sickness_history') == 'on'
                profile.medical_conditions = request.POST.get('medical_conditions', '')
                profile.medications = request.POST.get('medications', '')
                profile.save()
                messages.success(request, 'Altitude profile updated successfully!')
            else:
                # Create new profile
                AltitudeProfile.objects.create(
                    user=request.user,
                    age=request.POST.get('age'),
                    fitness_level=request.POST.get('fitness_level'),
                    previous_altitude_experience=request.POST.get('previous_altitude_experience') == 'on',
                    max_altitude_reached=request.POST.get('max_altitude_reached', 0),
                    has_altitude_sickness_history=request.POST.get('has_altitude_sickness_history') == 'on',
                    medical_conditions=request.POST.get('medical_conditions', ''),
                    medications=request.POST.get('medications', '')
                )
                messages.success(request, 'Altitude profile created successfully!')
            
            return redirect('altitude_dashboard')
        except Exception as e:
            messages.error(request, f'Error saving profile: {str(e)}')
    
    context = {
        'profile': profile
    }
    
    return render(request, 'altitude/create_profile.html', context)

@login_required
def acclimatization_planner(request):
    """Create acclimatization plan for a trek"""
    if request.method == 'POST':
        try:
            # Get user's risk level
            try:
                altitude_profile = AltitudeProfile.objects.get(user=request.user)
                risk_level = altitude_profile.get_risk_level()
            except AltitudeProfile.DoesNotExist:
                risk_level = 'medium'  # Default if no profile
            
            plan = AcclimatizationPlan.objects.create(
                user=request.user,
                trek_name=request.POST.get('trek_name'),
                start_altitude=request.POST.get('start_altitude'),
                target_altitude=request.POST.get('target_altitude'),
                trek_duration=request.POST.get('trek_duration'),
                risk_level=risk_level
            )
            
            messages.success(request, f'Acclimatization plan created for {plan.trek_name}!')
            return redirect('view_acclimatization_plan', plan_id=plan.id)
            
        except Exception as e:
            messages.error(request, f'Error creating plan: {str(e)}')
    
    # Get user's altitude profile for risk assessment
    try:
        altitude_profile = AltitudeProfile.objects.get(user=request.user)
    except AltitudeProfile.DoesNotExist:
        altitude_profile = None

    # Fetch actual treks from DB for the selector
    from .models import Trekking, PeakClimbing
    treks = Trekking.objects.filter(is_active=True).values('id', 'title', 'max_altitude', 'duration')
    peaks = PeakClimbing.objects.filter(is_active=True).values('id', 'title', 'height', 'duration')

    context = {
        'altitude_profile': altitude_profile,
        'treks': list(treks),
        'peaks': list(peaks),
    }

    return render(request, 'altitude/acclimatization_planner.html', context)

@login_required
def view_acclimatization_plan(request, plan_id):
    """View detailed acclimatization plan"""
    plan = get_object_or_404(AcclimatizationPlan, id=plan_id, user=request.user)
    schedule = plan.generate_schedule()
    
    context = {
        'plan': plan,
        'schedule': schedule
    }
    
    return render(request, 'altitude/view_plan.html', context)

@login_required
def symptom_checker(request):
    """Daily symptom checker and logger"""
    if request.method == 'POST':
        try:
            # Get active plan — prefer one matching trek_name if provided
            trek_name = request.POST.get('trek_name', '')
            if trek_name:
                active_plan = AcclimatizationPlan.objects.filter(
                    user=request.user,
                    trek_name=trek_name,
                    is_active=True,
                ).first()
                # Auto-create plan if booking exists but no plan yet
                if not active_plan:
                    from .models import Trekking
                    import re
                    trek = Trekking.objects.filter(title=trek_name).first()
                    if trek:
                        def parse_alt(s):
                            m = re.search(r'(\d[\d,]+)', s or '')
                            return int(m.group(1).replace(',','')) if m else 5000
                        def parse_dur(s):
                            m = re.search(r'(\d+)', s or '')
                            return int(m.group(1)) if m else 14
                        active_plan = AcclimatizationPlan.objects.create(
                            user=request.user,
                            trek_name=trek_name,
                            start_altitude=1400,
                            target_altitude=parse_alt(trek.max_altitude),
                            trek_duration=parse_dur(trek.duration),
                            risk_level='medium',
                            is_active=True,
                        )
            else:
                active_plan = AcclimatizationPlan.objects.filter(
                    user=request.user, is_active=True
                ).first()
            
            symptom_log = SymptomLog.objects.create(
                user=request.user,
                acclimatization_plan=active_plan,
                current_altitude=request.POST.get('current_altitude'),
                headache=request.POST.get('headache', 0),
                nausea=request.POST.get('nausea', 0),
                fatigue=request.POST.get('fatigue', 0),
                dizziness=request.POST.get('dizziness', 0),
                sleep_difficulty=request.POST.get('sleep_difficulty', 0),
                appetite_loss=request.POST.get('appetite_loss', 0),
                confusion=request.POST.get('confusion') == 'on',
                difficulty_walking=request.POST.get('difficulty_walking') == 'on',
                shortness_of_breath_at_rest=request.POST.get('shortness_of_breath_at_rest') == 'on',
                chest_tightness=request.POST.get('chest_tightness') == 'on',
                coughing_blood=request.POST.get('coughing_blood') == 'on',
                oxygen_saturation=request.POST.get('oxygen_saturation') or None,
                heart_rate=request.POST.get('heart_rate') or None,
                notes=request.POST.get('notes', '')
            )
            
            # Get recommendation
            recommendation = symptom_log.get_recommendation()
            
            messages.add_message(
                request, 
                messages.ERROR if recommendation['color'] == 'danger' else 
                messages.WARNING if recommendation['color'] == 'warning' else
                messages.INFO if recommendation['color'] == 'info' else messages.SUCCESS,
                f"{recommendation['action']}: {recommendation['message']}"
            )
            
            return redirect('symptom_history')
            
        except Exception as e:
            messages.error(request, f'Error logging symptoms: {str(e)}')
    
    # Get today's log if exists
    today_log = SymptomLog.objects.filter(
        user=request.user,
        date=timezone.now().date()
    ).first()

    # Active acclimatization plans for dynamic altitude suggestions
    active_plans = AcclimatizationPlan.objects.filter(
        user=request.user, is_active=True
    ).order_by('trek_name')

    # User's upcoming trekking bookings for context
    from .models import Booking, Trekking
    from datetime import date as date_cls
    trek_bookings = Booking.objects.filter(
        user=request.user,
        status='PAID',
        travel_date__gte=date_cls.today(),
    ).select_related('trekking', 'travel_package__destination').order_by('travel_date')[:5]

    context = {
        'today_log': today_log,
        'active_plans': active_plans,
        'trek_bookings': trek_bookings,
    }

    return render(request, 'altitude/symptom_checker.html', context)

@login_required
def symptom_history(request):
    """View symptom history and trends"""
    logs = SymptomLog.objects.filter(user=request.user).order_by('-date')
    
    # Prepare chart data
    chart_data = []
    for log in logs[:14]:  # Last 14 days
        chart_data.append({
            'date': log.date.strftime('%m/%d'),
            'altitude': log.current_altitude,
            'ams_score': log.get_ams_score(),
            'severity': log.get_severity_level()
        })
    
    chart_data.reverse()  # Chronological order for chart
    
    context = {
        'logs': logs,
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'altitude/symptom_history.html', context)

@login_required
def emergency_protocols(request):
    """View emergency descent protocols"""
    # Get current altitude from latest log
    latest_log = SymptomLog.objects.filter(user=request.user).order_by('-date').first()
    current_altitude = latest_log.current_altitude if latest_log else 0
    
    # Find relevant emergency protocols
    protocols = EmergencyProtocol.objects.filter(
        altitude_range_min__lte=current_altitude,
        altitude_range_max__gte=current_altitude
    )
    
    # If no specific protocol, get the closest one
    if not protocols and current_altitude > 0:
        protocols = EmergencyProtocol.objects.all().order_by(
            'altitude_range_min'
        )
    
    context = {
        'protocols': protocols,
        'current_altitude': current_altitude,
        'latest_log': latest_log
    }
    
    return render(request, 'altitude/emergency_protocols.html', context)

@login_required
def oxygen_tracker(request):
    """Oxygen saturation tracking and analysis"""
    # Get logs with oxygen data
    oxygen_logs = SymptomLog.objects.filter(
        user=request.user,
        oxygen_saturation__isnull=False
    ).order_by('-date')[:30]
    
    # Prepare chart data
    oxygen_data = []
    for log in reversed(oxygen_logs):
        oxygen_data.append({
            'date': log.date.strftime('%m/%d'),
            'altitude': log.current_altitude,
            'oxygen_saturation': log.oxygen_saturation,
            'heart_rate': log.heart_rate or 0
        })
    
    # Calculate averages and trends
    if oxygen_logs:
        avg_oxygen = sum(log.oxygen_saturation for log in oxygen_logs) / len(oxygen_logs)
        latest_oxygen = oxygen_logs[0].oxygen_saturation
        
        # Determine oxygen status
        if latest_oxygen >= 95:
            oxygen_status = {'level': 'excellent', 'color': 'success', 'message': 'Excellent oxygen levels'}
        elif latest_oxygen >= 90:
            oxygen_status = {'level': 'good', 'color': 'info', 'message': 'Good oxygen levels'}
        elif latest_oxygen >= 85:
            oxygen_status = {'level': 'concerning', 'color': 'warning', 'message': 'Monitor closely - low oxygen'}
        else:
            oxygen_status = {'level': 'critical', 'color': 'danger', 'message': 'Critical - seek immediate help'}
    else:
        avg_oxygen = 0
        latest_oxygen = 0
        oxygen_status = {'level': 'no_data', 'color': 'secondary', 'message': 'No oxygen data recorded'}
    
    context = {
        'oxygen_logs': oxygen_logs,
        'oxygen_data': json.dumps(oxygen_data),
        'avg_oxygen': round(avg_oxygen, 1),
        'latest_oxygen': latest_oxygen,
        'oxygen_status': oxygen_status
    }
    
    return render(request, 'altitude/oxygen_tracker.html', context)


@login_required
def load_demo_data(request):
    """Seed realistic demo data for the logged-in user to showcase the altitude safety feature."""
    from django.utils import timezone
    from datetime import date, timedelta

    # 1. Create/update altitude profile
    AltitudeProfile.objects.update_or_create(
        user=request.user,
        defaults={
            'age': 28,
            'fitness_level': 'intermediate',
            'previous_altitude_experience': True,
            'max_altitude_reached': 3440,
            'has_altitude_sickness_history': False,
            'medical_conditions': '',
            'medications': '',
        }
    )

    # 2. Create an acclimatization plan — use actual trek from DB if available
    from .models import Trekking
    ebc = Trekking.objects.filter(title__icontains='Everest').first() \
          or Trekking.objects.filter(is_active=True).first()

    trek_name = ebc.title if ebc else 'High Altitude Trek'
    # Parse max altitude from trek (e.g. "5,545 m (Kala Patthar)" → 5545)
    import re
    target_alt = 5364
    if ebc and ebc.max_altitude:
        m = re.search(r'(\d[\d,]+)', ebc.max_altitude)
        if m:
            target_alt = int(m.group(1).replace(',', ''))

    plan, _ = AcclimatizationPlan.objects.get_or_create(
        user=request.user,
        trek_name=trek_name,
        defaults={
            'start_altitude': 2860,
            'target_altitude': target_alt,
            'trek_duration': 14,
            'risk_level': 'medium',
            'is_active': True,
        }
    )

    # 3. Seed 5 days of symptom logs (realistic progression)
    demo_logs = [
        # Day 1 — Lukla arrival, mild headache
        {'days_ago': 4, 'altitude': 2860, 'headache': 1, 'nausea': 0, 'fatigue': 1, 'dizziness': 0, 'sleep_difficulty': 1, 'appetite_loss': 0, 'oxygen_saturation': 94, 'heart_rate': 88, 'notes': 'Arrived Lukla. Mild headache, resting.'},
        # Day 2 — Namche, feeling better
        {'days_ago': 3, 'altitude': 3440, 'headache': 1, 'nausea': 0, 'fatigue': 1, 'dizziness': 0, 'sleep_difficulty': 0, 'appetite_loss': 0, 'oxygen_saturation': 91, 'heart_rate': 92, 'notes': 'Namche Bazaar. Acclimatization rest day.'},
        # Day 3 — Tengboche, moderate symptoms
        {'days_ago': 2, 'altitude': 3860, 'headache': 2, 'nausea': 1, 'fatigue': 2, 'dizziness': 1, 'sleep_difficulty': 1, 'appetite_loss': 1, 'oxygen_saturation': 88, 'heart_rate': 98, 'notes': 'Tengboche. Headache worsened after ascent.'},
        # Day 4 — Dingboche, improving
        {'days_ago': 1, 'altitude': 4410, 'headache': 1, 'nausea': 0, 'fatigue': 1, 'dizziness': 0, 'sleep_difficulty': 1, 'appetite_loss': 0, 'oxygen_saturation': 86, 'heart_rate': 102, 'notes': 'Dingboche. Feeling better after rest day.'},
        # Day 5 — today, current status
        {'days_ago': 0, 'altitude': 4940, 'headache': 2, 'nausea': 1, 'fatigue': 2, 'dizziness': 1, 'sleep_difficulty': 2, 'appetite_loss': 1, 'oxygen_saturation': 82, 'heart_rate': 108, 'notes': 'Lobuche. Significant fatigue and headache. Monitoring closely.'},
    ]

    for entry in demo_logs:
        log_date = date.today() - timedelta(days=entry['days_ago'])
        SymptomLog.objects.update_or_create(
            user=request.user,
            date=log_date,
            defaults={
                'acclimatization_plan': plan,
                'current_altitude': entry['altitude'],
                'headache': entry['headache'],
                'nausea': entry['nausea'],
                'fatigue': entry['fatigue'],
                'dizziness': entry['dizziness'],
                'sleep_difficulty': entry['sleep_difficulty'],
                'appetite_loss': entry['appetite_loss'],
                'oxygen_saturation': entry['oxygen_saturation'],
                'heart_rate': entry['heart_rate'],
                'notes': entry['notes'],
            }
        )

    messages.success(request, 'Demo data loaded — showing a simulated EBC trek progression over 5 days.')
    return redirect('altitude_dashboard')
