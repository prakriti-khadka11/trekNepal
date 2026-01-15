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
        'app.Booking',     # 🔑 link to existing booking app
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
