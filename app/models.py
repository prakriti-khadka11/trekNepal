from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Country(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='country_images/')
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('explore_country_detail', args=[str(self.id)])
    

class Destination(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='destinations/')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='destinations',null=True, blank=True)


    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('destination_detail', args=[str(self.id)])

class TourDetail(models.Model):
    title = models.CharField(max_length=255, default='Untitled')
    overview = models.TextField()
    highlight = models.TextField()
    itinerary = models.TextField(blank=True, null=True)
    cost_details = models.TextField()
    
    def __str__(self):
        return self.title

class TourImage(models.Model):
    tour_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tour_images/')

    def __str__(self):
        return f"Image for {self.tour_detail.title}"

class TravelPackage(models.Model):
    title = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="packages")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in days")
    available_seats = models.PositiveIntegerField()
    tour_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True, blank=True)
    featured_image = models.ImageField(upload_to="featured_images/", null=True, blank=True)
    short_description = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.title} - {self.destination.name}"
    
    def get_absolute_url(self):
        return reverse('travel_package_detail', args=[str(self.id)])


class PackageImage(models.Model):
    travel_package = models.ForeignKey('TravelPackage', related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='package_images/')

class PopularPlace(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to="popular_places/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     travel_package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, null=True, blank=True)
#     num_people = models.PositiveIntegerField(default=1)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     travel_date = models.DateField()
#     booking_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         if self.travel_package:
#             return f"{self.user.username} booked {self.travel_package.title} for {self.num_people} people"
#         return f"{self.user.username} booking"
    
#     def get_absolute_url(self):
#         return reverse('booking_detail', args=[str(self.id)])

# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     travel_package = models.ForeignKey(
#         TravelPackage, on_delete=models.CASCADE, null=True, blank=True
#     )
#     num_people = models.PositiveIntegerField(default=1)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     travel_date = models.DateField()
#     booking_date = models.DateTimeField(auto_now_add=True)

#     # ✅ ADD THESE
#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ("PENDING", "Pending"),
#             ("PAID", "Paid"),
#             ("FAILED", "Failed"),
#         ],
#         default="PENDING"
#     )
#     khalti_pidx = models.CharField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         if self.travel_package:
#             return f"{self.user.username} booked {self.travel_package.title} ({self.status})"
#         return f"{self.user.username} booking ({self.status})"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_package = models.ForeignKey(
        TravelPackage, on_delete=models.CASCADE, null=True, blank=True
    )
    num_people = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)

    # Existing fields
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("FAILED", "Failed"),
        ],
        default="PENDING"
    )
    khalti_pidx = models.CharField(max_length=100, blank=True, null=True)

    # ✅ Add these
    guide = models.ForeignKey('Guide', on_delete=models.SET_NULL, null=True, blank=True)
    guide_rating = models.PositiveSmallIntegerField(null=True, blank=True)

    # Trekking booking support
    trekking = models.ForeignKey('Trekking', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    trek_date = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.travel_package:
            return f"{self.user.username} booked {self.travel_package.title} ({self.status})"
        return f"{self.user.username} booking ({self.status})"



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name="reviews", blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}/5"

class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class SliderImage(models.Model):
    image = models.ImageField(upload_to='slider_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Slider Image {self.id}"

class Trekking(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    max_altitude = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    itinerary = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='trekking/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('trekking_detail', args=[str(self.slug)])

class PeakClimbing(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    height = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    itinerary = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='peak_climbing/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('peak_climbing_detail', args=[str(self.slug)])

class TrekkingGalleryImage(models.Model):
    trekking = models.ForeignKey(Trekking, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='trekking/gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Gallery image for {self.trekking.title}"

class PeakClimbingGalleryImage(models.Model):
    peak = models.ForeignKey(PeakClimbing, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='peak_climbing/gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Gallery image for {self.peak.title}"

class PeakClimbingBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    peak_climbing = models.ForeignKey(PeakClimbing, on_delete=models.CASCADE)
    num_people = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    climbing_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} booked {self.peak_climbing.title} for {self.num_people} people"
    
    def get_absolute_url(self):
        return reverse('booking_confirmation')
    

class DestinationGalleryImage(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='destinations/gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Gallery image for {self.destination.name}"
    

# guide

from django.db import models
from django.contrib.auth.models import User


# class Guide(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     license_certificate = models.FileField(upload_to="guides/certificates/")
#     verified = models.BooleanField(default=False)

#     bio = models.TextField(blank=True, null=True)
#     experience_years = models.IntegerField(default=0)
#     languages = models.CharField(max_length=255, blank=True)  
#     profile_picture = models.ImageField(upload_to="guides/profiles/", blank=True, null=True)

#     def __str__(self):
#         return self.user.username


from django.db import models

# Create your models here.
# models.py
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verification_code = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)

# Added

class Guide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_certificate = models.FileField(upload_to="guides/certificates/")
    verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    languages = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to="guides/profiles/", blank=True, null=True)

    def average_rating(self):
        from django.db.models import Avg
        return self.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    def __str__(self):
        return self.user.username


class GuideReview(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guide.user.username} - {self.rating}/5"


# Personal Features Models
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default='fas fa-money-bill')
    color = models.CharField(max_length=7, default='#667eea')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Expense Categories"

class TravelExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NPR')
    date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Booking integration fields
    is_booking_expense = models.BooleanField(default=False)
    booking_id = models.IntegerField(null=True, blank=True)  # Reference to booking without FK
    
    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"
    
    class Meta:
        ordering = ['-date', '-created_at']

class TravelBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NPR')
    start_date = models.DateField()
    end_date = models.DateField()
    destination = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def spent_amount(self):
        from .models import TravelExpense
        expenses = TravelExpense.objects.filter(
            user=self.user,
            date__range=[self.start_date, self.end_date]
        )
        # Also include expenses for this destination
        destination_expenses = expenses.filter(location__icontains=self.destination)
        return sum(expense.amount for expense in destination_expenses)
    
    def remaining_budget(self):
        return self.total_budget - self.spent_amount()
    
    def budget_percentage(self):
        if self.total_budget > 0:
            return (self.spent_amount() / self.total_budget) * 100
        return 0
    
    def get_budget_status(self):
        percentage = self.budget_percentage()
        if percentage >= 100:
            return 'over_budget'
        elif percentage >= 90:
            return 'critical'
        elif percentage >= 75:
            return 'warning'
        else:
            return 'good'
    
    def __str__(self):
        return f"{self.title} - {self.destination}"

class TravelWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='NPR')
    priority = models.CharField(max_length=10, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    target_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.destination}, {self.country}"
    
    class Meta:
        ordering = ['-priority', 'target_date']

class TravelDocument(models.Model):
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('insurance', 'Travel Insurance'),
        ('ticket', 'Flight Ticket'),
        ('hotel', 'Hotel Booking'),
        ('permit', 'Trekking Permit'),
        ('vaccination', 'Vaccination Certificate'),
        ('other', 'Other')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=100)
    document_number = models.CharField(max_length=50, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issuing_authority = models.CharField(max_length=100, blank=True)
    document_file = models.FileField(upload_to='documents/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expiring_soon(self):
        if self.expiry_date:
            from django.utils import timezone
            days_until_expiry = (self.expiry_date - timezone.now().date()).days
            return days_until_expiry <= 30
        return False
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.title}"
    
    class Meta:
        ordering = ['expiry_date', '-created_at']

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_currency = models.CharField(max_length=3, default='NPR')
    budget_alerts = models.BooleanField(default=True)
    document_expiry_alerts = models.BooleanField(default=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_email = models.EmailField(blank=True)
    travel_style = models.CharField(max_length=20, choices=[
        ('budget', 'Budget Traveler'),
        ('comfort', 'Comfort Traveler'),
        ('luxury', 'Luxury Traveler'),
        ('adventure', 'Adventure Seeker')
    ], default='comfort')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


# Altitude Sickness Prevention System Models
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


# Custom Package Request System Models
class CustomPackageRequest(models.Model):
    """Model for users to request custom travel packages"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWING', 'Under Review'),
        ('QUOTED', 'Quote Sent'),
        ('ACCEPTED', 'Quote Accepted'),
        ('REJECTED', 'Rejected'),
        ('CONVERTED', 'Converted to Booking'),
    ]
    
    ACTIVITY_CHOICES = [
        ('trekking', 'Trekking'),
        ('peak_climbing', 'Peak Climbing'),
        ('tour', 'Cultural Tour'),
        ('wildlife', 'Wildlife Safari'),
        ('pilgrimage', 'Pilgrimage'),
        ('adventure', 'Adventure Sports'),
        ('mixed', 'Mixed Activities'),
    ]
    
    # User information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_requests')
    
    # Request details
    destination = models.CharField(max_length=255, help_text="Desired destination")
    alternative_destinations = models.TextField(blank=True, help_text="Alternative destinations (comma separated)")
    
    # Travel details
    preferred_start_date = models.DateField(help_text="Preferred start date")
    preferred_end_date = models.DateField(help_text="Preferred end date")
    flexible_dates = models.BooleanField(default=False, help_text="Are dates flexible?")
    
    num_travelers = models.PositiveIntegerField(default=1, help_text="Number of travelers")
    
    # Budget
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum budget per person")
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum budget per person")
    currency = models.CharField(max_length=3, default='USD')
    
    # Preferences
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='mixed')
    accommodation_preference = models.CharField(max_length=50, blank=True, help_text="e.g., Hotel, Lodge, Camping")
    guide_required = models.BooleanField(default=True)
    
    # Special requirements
    special_requirements = models.TextField(blank=True, help_text="Dietary restrictions, accessibility needs, etc.")
    additional_notes = models.TextField(blank=True, help_text="Any other information")
    
    # File uploads
    inspiration_image = models.ImageField(upload_to='custom_requests/', blank=True, null=True, help_text="Upload inspiration photos")
    reference_document = models.FileField(upload_to='custom_requests/docs/', blank=True, null=True, help_text="Upload itinerary ideas")
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    
    # Admin notes
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Custom Package Request'
        verbose_name_plural = 'Custom Package Requests'
    
    def __str__(self):
        return f"{self.user.username} - {self.destination} ({self.get_status_display()})"
    
    def get_duration_days(self):
        """Calculate trip duration in days"""
        if self.preferred_start_date and self.preferred_end_date:
            return (self.preferred_end_date - self.preferred_start_date).days
        return 0
    
    def get_total_budget_range(self):
        """Calculate total budget range for all travelers"""
        return {
            'min': self.budget_min * self.num_travelers,
            'max': self.budget_max * self.num_travelers
        }


class RequestQuote(models.Model):
    """Admin-created quotes for custom package requests"""
    custom_request = models.ForeignKey(CustomPackageRequest, on_delete=models.CASCADE, related_name='quotes')
    
    # Quote details
    package_title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed package description")
    itinerary = models.TextField(help_text="Day-by-day itinerary")
    
    # Pricing
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Inclusions/Exclusions
    inclusions = models.TextField(help_text="What's included (one per line)")
    exclusions = models.TextField(blank=True, help_text="What's not included (one per line)")
    
    # Terms
    validity_days = models.PositiveIntegerField(default=7, help_text="Quote valid for how many days")
    terms_and_conditions = models.TextField(blank=True)
    
    # Payment terms
    advance_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100, help_text="Advance payment %")
    cancellation_policy = models.TextField(blank=True)
    confirmed_travel_date = models.DateField(null=True, blank=True, help_text="Confirmed travel date agreed with user")
    
    # Status
    is_active = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quote for {self.custom_request.user.username} - {self.package_title}"
    
    def is_expired(self):
        """Check if quote has expired"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def get_advance_amount(self):
        """Calculate advance payment amount"""
        return (self.total_price * self.advance_payment_percentage) / 100


class RequestMessage(models.Model):
    """Messages/communication between user and admin regarding custom requests"""
    custom_request = models.ForeignKey(CustomPackageRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    
    message = models.TextField()
    attachment = models.FileField(upload_to='request_messages/', blank=True, null=True)
    
    is_admin_message = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sender_type = "Admin" if self.is_admin_message else "User"
        return f"{sender_type} message for Request #{self.custom_request.id}"


class GuideMessage(models.Model):
    """Messages between users and guides for their bookings"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='guide_messages/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} for Booking #{self.booking.id}"


# ── Packing List Generator ──────────────────────────────────────────────────

ITEM_CATEGORIES = [
    ('clothing',    'Clothing'),
    ('footwear',    'Footwear'),
    ('gear',        'Gear & Equipment'),
    ('health',      'Health & Safety'),
    ('documents',   'Documents & Money'),
    ('food_water',  'Food & Water'),
    ('electronics', 'Electronics'),
    ('camping',     'Camping Gear'),
    ('climbing',    'Climbing Gear'),
    ('seasonal',    'Seasonal Extras'),
    ('destination', 'Destination Specifics'),
]

ITEM_PRIORITY = [
    ('essential',    'Essential'),
    ('recommended',  'Recommended'),
    ('optional',     'Optional'),
]


class PackingTemplate(models.Model):
    """
    Pre-defined packing item catalogue.
    One row = one item for a trip_type + season combination.
    Seeded via: python manage.py seed_packing_templates
    """
    TRIP_TYPES = [
        ('easy',          'Easy Trek / Tour'),
        ('moderate',      'Moderate Trek'),
        ('high_altitude', 'High Altitude Trek'),
        ('peak_climbing', 'Peak Climbing'),
    ]
    SEASONS = [
        ('spring',  'Spring (Mar–May)'),
        ('monsoon', 'Monsoon (Jun–Aug)'),
        ('autumn',  'Autumn (Sep–Nov)'),
        ('winter',  'Winter (Dec–Feb)'),
        ('all',     'All Seasons'),
    ]

    trip_type  = models.CharField(max_length=20, choices=TRIP_TYPES)
    season     = models.CharField(max_length=10, choices=SEASONS)
    category   = models.CharField(max_length=20, choices=ITEM_CATEGORIES)
    name       = models.CharField(max_length=200)
    priority   = models.CharField(max_length=15, choices=ITEM_PRIORITY, default='essential')
    quantity   = models.PositiveSmallIntegerField(default=1)
    per_person = models.BooleanField(default=False)
    notes      = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['trip_type', 'season', 'category', '-priority', 'name']

    def __str__(self):
        return f'[{self.trip_type}/{self.season}] {self.name}'
