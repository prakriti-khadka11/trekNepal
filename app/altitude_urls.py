from django.urls import path
from . import altitude_views

urlpatterns = [
    # Main dashboard
    path('', altitude_views.altitude_dashboard, name='altitude_dashboard'),
    
    # Profile management
    path('profile/create/', altitude_views.create_altitude_profile, name='create_altitude_profile'),
    
    # Acclimatization planning
    path('planner/', altitude_views.acclimatization_planner, name='acclimatization_planner'),
    path('plan/<int:plan_id>/', altitude_views.view_acclimatization_plan, name='view_acclimatization_plan'),
    
    # Symptom tracking
    path('symptoms/', altitude_views.symptom_checker, name='symptom_checker'),
    path('symptoms/history/', altitude_views.symptom_history, name='symptom_history'),
    
    # Emergency protocols
    path('emergency/', altitude_views.emergency_protocols, name='emergency_protocols'),
    
    # Oxygen tracking
    path('oxygen/', altitude_views.oxygen_tracker, name='oxygen_tracker'),
    path('demo/', altitude_views.load_demo_data, name='altitude_demo'),
]