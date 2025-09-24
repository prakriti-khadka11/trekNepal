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
