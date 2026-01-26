from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class EmergencyAlert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('raised', 'Raised'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    booking = models.ForeignKey(
        'app.Booking',     
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    emergency_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    location = models.CharField(max_length=255)

    message = models.TextField(blank=True)

    # Optional health snapshot (NO health app needed)
    symptoms = models.TextField(blank=True)
    altitude = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='raised')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.emergency_type}"

# New Database Models for Emergency Data
class District(models.Model):
    """Nepal Districts with emergency information"""
    name = models.CharField(max_length=100, unique=True)
    province = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class EmergencyContact(models.Model):
    """Emergency contact numbers for districts"""
    CONTACT_TYPES = [
        ('police', 'Police'),
        ('hospital', 'Hospital'),
        ('fire_brigade', 'Fire Brigade'),
        ('ambulance', 'Ambulance'),
        ('tourist_police', 'Tourist Police'),
        ('rescue', 'Rescue Service'),
    ]
    
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='emergency_contacts')
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES)
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.district.name} - {self.get_contact_type_display()}: {self.phone_number}"
    
    class Meta:
        ordering = ['district__name', 'contact_type']

class Hospital(models.Model):
    """Hospital information with location data"""
    name = models.CharField(max_length=200)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='hospitals')
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Location coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    
    # Hospital details
    specializations = models.TextField(blank=True, help_text="Comma-separated specializations")
    has_emergency_ward = models.BooleanField(default=True)
    has_icu = models.BooleanField(default=False)
    has_ambulance = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.district.name}"
    
    class Meta:
        ordering = ['district__name', 'name']

class UniversalEmergencyNumber(models.Model):
    """Universal emergency numbers for Nepal"""
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name}: {self.number}"
