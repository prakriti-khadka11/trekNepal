from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class AltitudeProfile(models.Model):
    """User's altitude sickness risk profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    fitness_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], default='intermediate')
    previous_altitude_experience = models.BooleanField(default=False)
    max_altitude_reached = models.IntegerField(default=0, help_text="Maximum altitude reached in meters")
    has_altitude_sickness_history = models.BooleanField(default=False)
    medical_conditions = models.TextField(blank=True, help_text="Heart, lung, or other relevant conditions")
    medications = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_risk_level(self):
        """Calculate altitude sickness risk level"""
        risk_score = 0
        
        # Age factor
        if self.age > 50:
            risk_score += 2
        elif self.age > 40:
            risk_score += 1
            
        # Experience factor
        if not self.previous_altitude_experience:
            risk_score += 2
        elif self.max_altitude_reached < 3000:
            risk_score += 1
            
        # Medical history
        if self.has_altitude_sickness_history:
            risk_score += 3
            
        # Fitness level
        if self.fitness_level == 'beginner':
            risk_score += 2
        elif self.fitness_level == 'intermediate':
            risk_score += 1
            
        if risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def __str__(self):
        return f"{self.user.username}'s Altitude Profile"

class AcclimatizationPlan(models.Model):
    """Generated acclimatization schedule for a trek"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trek_name = models.CharField(max_length=200)
    start_altitude = models.IntegerField(help_text="Starting altitude in meters")
    target_altitude = models.IntegerField(help_text="Target altitude in meters")
    trek_duration = models.IntegerField(help_text="Trek duration in days")
    risk_level = models.CharField(max_length=10, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def generate_schedule(self):
        """Generate day-by-day acclimatization schedule"""
        schedule = []
        current_altitude = self.start_altitude
        altitude_gain_per_day = 300 if self.risk_level == 'high' else 400 if self.risk_level == 'medium' else 500
        
        for day in range(1, self.trek_duration + 1):
            if day == 1:
                schedule.append({
                    'day': day,
                    'altitude': current_altitude,
                    'activity': 'Arrival and rest',
                    'notes': 'Hydrate well, avoid alcohol, light activities only'
                })
            else:
                # Calculate safe altitude gain
                if current_altitude >= 3000:  # Above 3000m, be more careful
                    if day % 3 == 0:  # Rest day every 3rd day above 3000m
                        schedule.append({
                            'day': day,
                            'altitude': current_altitude,
                            'activity': 'Acclimatization rest day',
                            'notes': 'Stay at same altitude, light hiking, monitor symptoms'
                        })
                    else:
                        current_altitude += altitude_gain_per_day
                        schedule.append({
                            'day': day,
                            'altitude': min(current_altitude, self.target_altitude),
                            'activity': 'Ascent day',
                            'notes': f'Climb high, sleep low principle. Max gain: {altitude_gain_per_day}m'
                        })
                else:
                    current_altitude += altitude_gain_per_day * 1.5  # Can climb faster below 3000m
                    schedule.append({
                        'day': day,
                        'altitude': min(current_altitude, self.target_altitude),
                        'activity': 'Normal trekking',
                        'notes': 'Monitor for early symptoms, stay hydrated'
                    })
                    
                if current_altitude >= self.target_altitude:
                    break
                    
        return schedule
    
    def __str__(self):
        return f"{self.trek_name} - {self.user.username}"

class SymptomLog(models.Model):
    """Daily symptom tracking during trek"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acclimatization_plan = models.ForeignKey(AcclimatizationPlan, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    current_altitude = models.IntegerField()
    
    # Altitude sickness symptoms (0-3 scale: None, Mild, Moderate, Severe)
    headache = models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    nausea = models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    fatigue = models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    dizziness = models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    sleep_difficulty = models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    appetite_loss = models.IntegerField(default=0, choices=[(0, 'None'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    
    # Severe symptoms (HACE/HAPE indicators)
    confusion = models.BooleanField(default=False)
    difficulty_walking = models.BooleanField(default=False)
    shortness_of_breath_at_rest = models.BooleanField(default=False)
    chest_tightness = models.BooleanField(default=False)
    coughing_blood = models.BooleanField(default=False)
    
    # Vitals
    oxygen_saturation = models.IntegerField(null=True, blank=True, help_text="SpO2 percentage")
    heart_rate = models.IntegerField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_ams_score(self):
        """Calculate Acute Mountain Sickness score"""
        return self.headache + self.nausea + self.fatigue + self.dizziness + self.sleep_difficulty + self.appetite_loss
    
    def get_severity_level(self):
        """Determine severity level"""
        ams_score = self.get_ams_score()
        has_severe_symptoms = any([
            self.confusion, self.difficulty_walking, 
            self.shortness_of_breath_at_rest, self.chest_tightness, self.coughing_blood
        ])
        
        if has_severe_symptoms or ams_score >= 12:
            return 'severe'  # HACE/HAPE - Emergency descent needed
        elif ams_score >= 6:
            return 'moderate'  # Stop ascent, consider descent
        elif ams_score >= 3:
            return 'mild'  # Monitor closely, slow ascent
        else:
            return 'none'
    
    def get_recommendation(self):
        """Get medical recommendation based on symptoms"""
        severity = self.get_severity_level()
        
        if severity == 'severe':
            return {
                'action': 'EMERGENCY DESCENT',
                'message': 'Immediate descent required. Seek medical attention.',
                'color': 'danger'
            }
        elif severity == 'moderate':
            return {
                'action': 'STOP ASCENT',
                'message': 'Do not ascend. Rest and monitor. Consider descent if no improvement.',
                'color': 'warning'
            }
        elif severity == 'mild':
            return {
                'action': 'MONITOR CLOSELY',
                'message': 'Ascend slowly. Take rest day if symptoms worsen.',
                'color': 'info'
            }
        else:
            return {
                'action': 'CONTINUE SAFELY',
                'message': 'No altitude sickness detected. Continue with planned schedule.',
                'color': 'success'
            }
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.current_altitude}m"

class EmergencyProtocol(models.Model):
    """Emergency descent protocols and contacts"""
    altitude_range_min = models.IntegerField()
    altitude_range_max = models.IntegerField()
    location_name = models.CharField(max_length=200)
    
    # Emergency contacts
    rescue_contact = models.CharField(max_length=50)
    helicopter_service = models.CharField(max_length=50, blank=True)
    nearest_hospital = models.CharField(max_length=200)
    
    # Descent information
    descent_route = models.TextField()
    safe_altitude = models.IntegerField(help_text="Safe altitude to descend to")
    estimated_descent_time = models.CharField(max_length=100)
    
    # Medical facilities
    oxygen_availability = models.BooleanField(default=False)
    medical_post_location = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.location_name} ({self.altitude_range_min}-{self.altitude_range_max}m)"