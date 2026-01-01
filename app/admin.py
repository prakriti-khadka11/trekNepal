
from django.contrib import admin
from .models import Booking, ContactUs, Destination, Review, SliderImage, TourDetail, TravelPackage, Country, Trekking, PeakClimbing
from .models import (
    TourImage, PackageImage, DestinationGalleryImage,
    TrekkingGalleryImage, PeakClimbingGalleryImage
)

# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_package', 'num_people', 'total_price', 'travel_date', 'booking_date')
    list_filter = ('travel_date', 'booking_date', 'travel_package')
    search_fields = ('user__username', 'travel_package__title')

# Contact Us Admin
@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email')

# Destination Admin
@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'description')
    list_filter = ('location',)
    search_fields = ('name', 'location')

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_package', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('user__username', 'travel_package__title')

# Slider Image Admin
@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'caption')
    search_fields = ('caption',)

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

@admin.register(TourDetail)
class TourDetailAdmin(admin.ModelAdmin):
    list_display = ('title', 'overview', 'highlight','itinerary', 'cost_details')
    search_fields = ('title',)
    inlines = [TourImageInline]



class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 1

@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'price', 'duration', 'available_seats')
    list_filter = ('destination', 'price')
    search_fields = ('title', 'destination__name')
    inlines = [PackageImageInline]


# Country Admin
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class TrekkingGalleryInline(admin.TabularInline):
    model = TrekkingGalleryImage
    extra = 1

@admin.register(Trekking)
class TrekkingAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'difficulty', 'price')
    list_filter = ('country', 'difficulty', 'price')
    search_fields = ('title', 'country')
    inlines = [TrekkingGalleryInline]


class PeakClimbingGalleryInline(admin.TabularInline):
    model = PeakClimbingGalleryImage
    extra = 1

@admin.register(PeakClimbing)
class PeakClimbingAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'difficulty', 'price')
    list_filter = ('country', 'difficulty', 'price')
    search_fields = ('title', 'country')
    inlines = [PeakClimbingGalleryInline]


# Add this to your admin.py file

from .models import DestinationGalleryImage

class DestinationGalleryInline(admin.TabularInline):
    model = DestinationGalleryImage
    extra = 1

class DestinationAdmin(admin.ModelAdmin):
    inlines = [DestinationGalleryInline]
    list_display = ('name', 'location', 'description')
    search_fields = ('name', 'location')

# Re-register the Destination model with the updated admin class
admin.site.unregister(Destination)
admin.site.register(Destination, DestinationAdmin)

# Guide

from django.contrib import admin
from .models import Guide

# @admin.register(Guide)
# class GuideAdmin(admin.ModelAdmin):
#     list_display = ("user", "verified")
#     list_filter = ("verified",)
#     search_fields = ("user__username", "user__email")

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = (
        "user", 
        "verified", 
        "experience_years", 
        "languages", 
        "license_certificate", 
        "profile_picture"
    )
    list_filter = ("verified",)
    search_fields = ("user__username", "user__email", "languages")
    readonly_fields = ("profile_picture", "license_certificate")

    actions = ["approve_guides"]

    # Admin action to approve selected guides
    def approve_guides(self, request, queryset):
        updated = queryset.update(verified=True)
        self.message_user(request, f"{updated} guide(s) successfully approved.")
    approve_guides.short_description = "Approve selected guides"

