from django.contrib import admin
from .models import (
    Booking, ContactUs, Destination, Review, SliderImage, TourDetail, TravelPackage, Country, 
    Trekking, PeakClimbing, TourImage, PackageImage, DestinationGalleryImage,
    TrekkingGalleryImage, PeakClimbingGalleryImage, PopularPlace, PeakClimbingBooking,
    Profile, Guide, GuideReview, ExpenseCategory, TravelExpense, TravelBudget, 
    TravelWishlist, TravelDocument, UserPreference, AltitudeProfile, 
    AcclimatizationPlan, SymptomLog, EmergencyProtocol, CustomPackageRequest,
    RequestQuote, RequestMessage, GuideMessage
)

# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_package', 'num_people', 'total_price', 'travel_date', 'booking_date', 'status')
    list_filter = ('travel_date', 'booking_date', 'travel_package', 'status')
    search_fields = ('user__username', 'travel_package__title', 'khalti_pidx')
    readonly_fields = ('khalti_pidx',)

# Contact Us Admin
@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email')

# Destination Admin
@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'country')
    list_filter = ('location', 'country')
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
    list_display = ('title', 'country', 'difficulty', 'price', 'is_active')
    list_filter = ('country', 'difficulty', 'price', 'is_active')
    search_fields = ('title', 'country')
    inlines = [TrekkingGalleryInline]

class PeakClimbingGalleryInline(admin.TabularInline):
    model = PeakClimbingGalleryImage
    extra = 1

@admin.register(PeakClimbing)
class PeakClimbingAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'difficulty', 'price', 'is_active')
    list_filter = ('country', 'difficulty', 'price', 'is_active')
    search_fields = ('title', 'country')
    inlines = [PeakClimbingGalleryInline]

class DestinationGalleryInline(admin.TabularInline):
    model = DestinationGalleryImage
    extra = 1

# Popular Places Admin
@admin.register(PopularPlace)
class PopularPlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'is_active', 'date_added')
    list_filter = ('is_active', 'date_added', 'destination')
    search_fields = ('title', 'destination__name')

# Peak Climbing Booking Admin
@admin.register(PeakClimbingBooking)
class PeakClimbingBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'peak_climbing', 'num_people', 'total_price', 'climbing_date', 'booking_date')
    list_filter = ('climbing_date', 'booking_date')
    search_fields = ('user__username', 'peak_climbing__title')

# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'email_verification_code')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__email')

# Guide Admin
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

# Guide Review Admin
@admin.register(GuideReview)
class GuideReviewAdmin(admin.ModelAdmin):
    list_display = ('guide', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('guide__user__username', 'user__username')

# ===== PERSONAL FEATURES ADMIN =====

# Expense Category Admin
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name',)

# Travel Expense Admin
@admin.register(TravelExpense)
class TravelExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category', 'amount', 'currency', 'date', 'location', 'is_booking_expense')
    list_filter = ('category', 'currency', 'date', 'is_booking_expense', 'created_at')
    search_fields = ('user__username', 'title', 'location')
    readonly_fields = ('created_at',)

# Travel Budget Admin
@admin.register(TravelBudget)
class TravelBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'destination', 'total_budget', 'currency', 'start_date', 'end_date', 'is_active')
    list_filter = ('currency', 'is_active', 'start_date', 'end_date')
    search_fields = ('user__username', 'title', 'destination')

# Travel Wishlist Admin
@admin.register(TravelWishlist)
class TravelWishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'country', 'priority', 'target_date', 'is_completed')
    list_filter = ('priority', 'is_completed', 'country', 'target_date')
    search_fields = ('user__username', 'destination', 'country')

# Travel Document Admin
@admin.register(TravelDocument)
class TravelDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'title', 'document_number', 'issue_date', 'expiry_date', 'issuing_authority')
    list_filter = ('document_type', 'issue_date', 'expiry_date')
    search_fields = ('user__username', 'title', 'document_number', 'issuing_authority')

# User Preference Admin
@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_currency', 'travel_style', 'budget_alerts', 'document_expiry_alerts')
    list_filter = ('preferred_currency', 'travel_style', 'budget_alerts', 'document_expiry_alerts')
    search_fields = ('user__username', 'emergency_contact_name')

# ===== ALTITUDE SAFETY ADMIN =====

# Altitude Profile Admin
@admin.register(AltitudeProfile)
class AltitudeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'fitness_level', 'max_altitude_reached', 'has_altitude_sickness_history', 'created_at')
    list_filter = ('fitness_level', 'has_altitude_sickness_history', 'previous_altitude_experience')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

# Acclimatization Plan Admin
@admin.register(AcclimatizationPlan)
class AcclimatizationPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'trek_name', 'start_altitude', 'target_altitude', 'trek_duration', 'risk_level', 'is_active')
    list_filter = ('risk_level', 'is_active', 'created_at')
    search_fields = ('user__username', 'trek_name')

# Symptom Log Admin
@admin.register(SymptomLog)
class SymptomLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'current_altitude', 'headache', 'nausea', 'fatigue', 'oxygen_saturation')
    list_filter = ('date', 'headache', 'nausea', 'fatigue', 'confusion', 'difficulty_walking')
    search_fields = ('user__username',)

# Emergency Protocol Admin
@admin.register(EmergencyProtocol)
class EmergencyProtocolAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'altitude_range_min', 'altitude_range_max', 'rescue_contact', 'nearest_hospital')
    list_filter = ('altitude_range_min', 'altitude_range_max', 'oxygen_availability')
    search_fields = ('location_name', 'rescue_contact', 'nearest_hospital')

# Custom Package Request Admin
@admin.register(CustomPackageRequest)
class CustomPackageRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'destination', 'num_travelers', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'activity_type', 'priority')
    search_fields = ('user__username', 'destination', 'special_requirements')
    readonly_fields = ('created_at', 'updated_at')

# Request Quote Admin
@admin.register(RequestQuote)
class RequestQuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'custom_request', 'package_title', 'total_price', 'is_active', 'accepted', 'created_at')
    list_filter = ('is_active', 'accepted', 'created_at')
    search_fields = ('package_title', 'custom_request__user__username')
    readonly_fields = ('created_at',)

# Request Message Admin
@admin.register(RequestMessage)
class RequestMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'custom_request', 'sender', 'is_admin_message', 'is_read', 'created_at')
    list_filter = ('is_admin_message', 'is_read', 'created_at')
    search_fields = ('sender__username', 'message')
    readonly_fields = ('created_at',)

# Guide Message Admin
@admin.register(GuideMessage)
class GuideMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'message', 'booking__id')
    readonly_fields = ('created_at',)
