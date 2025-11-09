from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

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

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, null=True, blank=True)
    num_people = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.travel_package:
            return f"{self.user.username} booked {self.travel_package.title} for {self.num_people} people"
        return f"{self.user.username} booking"
    
    def get_absolute_url(self):
        return reverse('booking_detail', args=[str(self.id)])

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


class Guide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_certificate = models.FileField(upload_to="guides/certificates/")
    verified = models.BooleanField(default=False)

    bio = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    languages = models.CharField(max_length=255, blank=True)  # e.g. "English, Nepali, French"
    profile_picture = models.ImageField(upload_to="guides/profiles/", blank=True, null=True)

    def __str__(self):
        return self.user.username

