from django import forms
from .models import Booking
from .models import PeakClimbingBooking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['num_people', 'travel_date']

class PeakClimbingBookingForm(forms.ModelForm):
    class Meta:
        model = PeakClimbingBooking
        fields = ['num_people', 'climbing_date']


# Guide


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Guide


class GuideRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    license_certificate = forms.FileField(required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    experience_years = forms.IntegerField(min_value=0, required=False)
    languages = forms.CharField(max_length=255, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Create or update related Guide profile
        guide = Guide.objects.create(
            user=user,
            license_certificate=self.cleaned_data["license_certificate"],
            bio=self.cleaned_data.get("bio", ""),
            experience_years=self.cleaned_data.get("experience_years", 0),
            languages=self.cleaned_data.get("languages", ""),
            profile_picture=self.cleaned_data.get("profile_picture", None),
            verified=False  # pending approval by admin
        )

        return user

# Guide Login Form
class GuideLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


# Guide Review Form
from .models import GuideReview

class GuideReviewForm(forms.ModelForm):
    class Meta:
        model = GuideReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience with this guide...',
                'class': 'form-control'
            })
        }
        labels = {
            'rating': 'How would you rate your guide?',
            'comment': 'Your Review (Optional)'
        }



# Custom Package Request Forms
from .models import CustomPackageRequest, RequestQuote, RequestMessage

class CustomPackageRequestForm(forms.ModelForm):
    class Meta:
        model = CustomPackageRequest
        fields = [
            'destination', 'alternative_destinations',
            'preferred_start_date', 'preferred_end_date', 'flexible_dates',
            'num_travelers', 'budget_min', 'budget_max',
            'activity_type', 'accommodation_preference', 'guide_required',
            'special_requirements', 'additional_notes',
            'inspiration_image', 'reference_document'
        ]
        widgets = {
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Everest Base Camp, Annapurna Circuit'
            }),
            'alternative_destinations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Alternative destinations (comma separated)'
            }),
            'preferred_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'preferred_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'flexible_dates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'num_travelers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum budget per person',
                'step': '0.01'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum budget per person',
                'step': '0.01'
            }),
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'accommodation_preference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3-star hotel, Mountain lodge'
            }),
            'guide_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dietary restrictions, medical conditions, accessibility needs, etc.'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any other information that would help us create your perfect trip'
            }),
            'inspiration_image': forms.FileInput(attrs={'class': 'form-control'}),
            'reference_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'destination': 'Primary Destination',
            'alternative_destinations': 'Alternative Destinations (Optional)',
            'preferred_start_date': 'Preferred Start Date',
            'preferred_end_date': 'Preferred End Date',
            'flexible_dates': 'My dates are flexible',
            'num_travelers': 'Number of Travelers',
            'budget_min': 'Minimum Budget (USD per person)',
            'budget_max': 'Maximum Budget (USD per person)',
            'activity_type': 'Type of Activity',
            'accommodation_preference': 'Accommodation Preference',
            'guide_required': 'I need a guide',
            'special_requirements': 'Special Requirements',
            'additional_notes': 'Additional Notes',
            'inspiration_image': 'Upload Inspiration Photo (Optional)',
            'reference_document': 'Upload Reference Document (Optional)',
        }


class RequestQuoteForm(forms.ModelForm):
    class Meta:
        model = RequestQuote
        fields = [
            'package_title', 'description', 'itinerary',
            'price_per_person', 'total_price',
            'inclusions', 'exclusions',
            'validity_days', 'terms_and_conditions',
            'confirmed_travel_date', 'cancellation_policy'
        ]
        widgets = {
            'package_title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'price_per_person': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inclusions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'exclusions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'validity_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'confirmed_travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cancellation_policy': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RequestMessageForm(forms.ModelForm):
    class Meta:
        model = RequestMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...'
            }),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'message': 'Message',
            'attachment': 'Attach File (Optional)',
        }
