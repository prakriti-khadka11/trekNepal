from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import TravelPackage, Booking,Review,ContactUs,SliderImage,Country,TourDetail,Trekking,PeakClimbing,PopularPlace,Destination,PeakClimbingBooking 
from .forms import BookingForm,PeakClimbingBookingForm
from django.db.models import Q
from django import forms
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from django.urls import reverse
from .utils import account_activation_token
import logging
from django.conf import settings

settings.KHALTI_SECRET_KEY
settings.KHALTI_PUBLIC_KEY

# Helper function to check if user is an admin
def home(request):
    # If user is logged in, check user type and redirect accordingly
    if request.user.is_authenticated:
        # Check if user is admin (superuser or staff)
        if request.user.is_superuser or request.user.is_staff:
            return redirect("admin_dashboard")
        # Check if user is a verified guide
        elif hasattr(request.user, 'guide') and request.user.guide.verified:
            return redirect("guide_dashboard")
    
    # Get featured destinations
    destinations = Destination.objects.all().order_by('-id')[:6]
    
    # Get popular packages
    packages = TravelPackage.objects.all().order_by('-id')[:6]
    
    # Get slider images
    slider_images = SliderImage.objects.all()[:3]
    
    # Print debug information
    print(f"Destinations count: {destinations.count()}")
    print(f"Packages count: {packages.count()}")
    
    context = {
        'destinations': destinations,
        'packages': packages,
        'slider_images': slider_images,
    }
    
    return render(request, 'home.html', context)


@login_required(login_url='login')
def destination_detail(request, id):
    destination = get_object_or_404(Destination, id=id)
    return render(request, 'destination_detail.html', {'destination': destination})


# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user has a guide profile
            if hasattr(user, 'guide'):
                # Guide trying to login through regular login - redirect to guide login
                messages.warning(request, "You are registered as a guide. Please use the guide login page.")
                return redirect("guide_login")
            
            # Regular user or admin login
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, "login.html")

    

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")



# Travel Package List
from django.shortcuts import render
from .models import TravelPackage

@login_required(login_url='login')
def package_list(request):
    packages = TravelPackage.objects.all()

    # Unique destinations
    destinations = TravelPackage.objects.values_list(
        'destination__name', flat=True
    ).distinct().order_by('destination__name')

    # Filters
    destination_filter = request.GET.get('destination')
    duration_filter = request.GET.get('duration')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if destination_filter:
        packages = packages.filter(destination__name=destination_filter)

    if duration_filter:
        if duration_filter == "1-3":
            packages = packages.filter(duration__gte=1, duration__lte=3)
        elif duration_filter == "4-7":
            packages = packages.filter(duration__gte=4, duration__lte=7)
        elif duration_filter == "8-14":
            packages = packages.filter(duration__gte=8, duration__lte=14)
        elif duration_filter == "15+":
            packages = packages.filter(duration__gte=15)

    if min_price:
        packages = packages.filter(price__gte=min_price)

    if max_price:
        packages = packages.filter(price__lte=max_price)

    return render(request, 'packages.html', {
        'packages': packages,
        'destinations': destinations,
    })


def booking_detail(request, id):
    booking = get_object_or_404(Booking, id=id)
    return render(request, 'booking_detail.html', {'booking': booking})

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        booking.delete()  # or booking.status = "cancelled"; booking.save()
        messages.success(request, "Your booking has been cancelled.")
        return redirect("my_bookings")
    return redirect("my_bookings")


# Edit profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("my_bookings")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "edit_profile.html", {"form": form})

@login_required
def book_travel(request, travel_id):
    travel_package = get_object_or_404(TravelPackage, id=travel_id)

    if request.method == "POST":
        num_people = int(request.POST["num_people"])
        travel_date = request.POST["travel_date"]
        total_price = travel_package.price * num_people  # Decimal

        # Store booking data in session temporarily (convert Decimal to float)
        request.session['pending_booking'] = {
            "travel_id": travel_package.id,
            "num_people": num_people,
            "travel_date": travel_date,
            "total_price": float(total_price),  # ✅ float for JSON
        }

        # Redirect to Khalti payment
        return redirect("khalti_initiate_temp")

    return render(request, "tour_detail.html", {"travel_package": travel_package})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "my_bookings.html", {"bookings": bookings})

@login_required
def booking_receipt(request, booking_id):
    """Display booking confirmation details (same as PDF email) in the system"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Import the dynamic details function
    from .utils import get_dynamic_booking_details
    dynamic_details = get_dynamic_booking_details(booking)
    
    # Generate the same data that goes into the PDF
    booking_details = {
        'booking_id': f'TNP-{booking.id}',
        'booking_date': booking.booking_date.date(),
        'payment_status': booking.status,
        'customer_name': booking.user.get_full_name() or booking.user.username,
        'customer_email': booking.user.email,
        'travel_date': booking.travel_date,
        'num_people': booking.num_people,
        'package_title': booking.travel_package.title,
        'destination': f"{dynamic_details['destination_info']['name']}, {dynamic_details['destination_info']['location']}",
        'hotel': dynamic_details['hotel'],
        'accommodation': dynamic_details['accommodation'],
        'ticket_no': dynamic_details['ticket_number'],
        'total_amount': booking.total_price,
        'payment_method': 'Khalti (Demo)',
        'transaction_id': booking.khalti_pidx,
        'destination_info': dynamic_details['destination_info']
    }
    
    return render(request, 'booking_receipt.html', {
        'booking': booking,
        'details': booking_details
    })


def user_data(request):
    users = User.objects.all()
    return render(request, "user_data.html", {"users": users})


@login_required
def travel_package_detail(request, travel_id):
    travel_package = get_object_or_404(TravelPackage, id=travel_id)
    tour_detail = travel_package.tour_detail
    images = travel_package.images.all()

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            user=request.user,
            travel_package=travel_package,
            rating=rating,
            comment=comment
        )
        return redirect('travel_package_detail', travel_id=travel_package.id)

    return render(request, 'travel_package_detail.html', {
        'travel_package': travel_package,
        'tour_detail': tour_detail,
        'images': images,
    })


from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ContactUs
from django.conf import settings

def contact_us(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'New Contact Message')
        message = request.POST.get('message')

        # Save to database
        ContactUs.objects.create(
            name=name,
            email=email,
            message=message
        )

        # Build email message
        email_subject = f"{subject}"
        email_message = (
            # f"Name: {name}\n"
            # f"Email: {email}\n\n"
            # f"Message:\n{message}"
            f"{message}"
        )

        # Send the email to yourself
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['prakritikhadka027@gmail.com'],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact_us')

    return render(request, 'contact_us.html')

def explore_countries(request):
    countries = Country.objects.all()
    return render(request, 'explore_countries.html', {'countries': countries})

from django.shortcuts import render, get_object_or_404
from .models import Country

# @login_required(login_url='login')
def explore_country_detail(request, id):
    country = get_object_or_404(Country, id=id)
    return render(request, 'explore_country_detail.html', {'country': country})


def search_view(request):
    query = request.GET.get('q', '')
    print("SEARCH QUERY:", query)  # Debug print

    if query:
        packages = TravelPackage.objects.filter(
            Q(title__icontains=query) | 
            Q(destination__name__icontains=query)
        )
    else:
        packages = TravelPackage.objects.none()

    return render(request, 'search_results.html', {
        'packages': packages,
        'query': query
    })


def tour_list(request):
    tours = TourDetail.objects.all()
    return render(request, 'tour_list.html', {'tours': tours})


@login_required(login_url='login')
def tour_detail(request, pk):
    tour = get_object_or_404(TourDetail, pk=pk)
    return render(request, 'tour_detail.html', {'tour': tour})

def trekking_list(request):
    treks = Trekking.objects.filter(is_active=True)
    return render(request, 'trekking_list.html', {'treks': treks})

@login_required(login_url='login')
def trekking_detail(request, slug):
    trek = get_object_or_404(Trekking, slug=slug)
    images = trek.gallery_images.all()
    return render(request, 'trekking_detail.html', {
        'trek': trek,
        'images': images,
    })

def peak_climbing_list(request):
    peaks = PeakClimbing.objects.filter(is_active=True)
    return render(request, 'peak_climbing_list.html', {'peaks': peaks})

# Detail view for each Peak Climbing
@login_required(login_url='login')
def peak_climbing_detail(request, slug):
    peak = get_object_or_404(PeakClimbing, slug=slug)
    return render(request, 'peak_climbing_detail.html', {'peak': peak})

@login_required
def book_peak_climbing(request, slug):
    peak = get_object_or_404(PeakClimbing, slug=slug)

    if request.method == 'POST':
        form = PeakClimbingBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.peak_climbing = peak
            booking.total_price = peak.price * form.cleaned_data['num_people']  # Total price calculation
            booking.save()
            return redirect('booking_confirmation')  # Redirect to a confirmation page after successful booking
    else:
        form = PeakClimbingBookingForm()

    return render(request, 'book_peak_climbing.html', {'peak': peak, 'form': form})

@login_required
def package_booking(request, package_id):
    package = get_object_or_404(TravelPackage, pk=package_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # ✅ Sets the user
            booking.travel_package = package
            booking.total_price = package.price * booking.num_people
            booking.save()
            return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'booking.html', {'form': form, 'package': package})


@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    peak_bookings = PeakClimbingBooking.objects.filter(user=request.user)
    return render(request, 'user_bookings.html', {
        'bookings': bookings,
        'peak_bookings': peak_bookings
    })


@login_required(login_url='login')  # redirect to login page if not logged in
def weather_view(request):
    return render(request, "weather.html")

@login_required(login_url='login')
def currency_converter(request):
    return render(request, "currency_converter.html")


def trek_map_view(request):
    return render(request, 'trek_map.html')

 # Guide

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Guide
from .forms import GuideRegisterForm, GuideLoginForm

from django.contrib import messages

def guide_register(request):
    if request.method == "POST":
        form = GuideRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Wait for admin approval before logging in.")
            return redirect("guide_login")
    else:
        form = GuideRegisterForm()
    return render(request, "guide_register.html", {"form": form})


def guide_login(request):
    if request.method == "POST":
        form = GuideLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, "guide"):
                if user.guide.verified:
                    login(request, user)
                    return redirect("guide_dashboard")  
                else:
                    messages.error(request, "Your account is pending admin approval.")
                    return redirect("guide_login")
            else:
                messages.error(request, "This is not a guide account.")
    else:
        form = GuideLoginForm()
    return render(request, "guide_login.html", {"form": form})


from .models import Guide

@login_required
def guide_dashboard(request):
    guide = Guide.objects.filter(user=request.user).first()
    
    if guide:
        # Get bookings assigned to this guide
        assigned_bookings = Booking.objects.filter(guide=guide).order_by('-booking_date')
        
        # Get booking statistics
        total_bookings = assigned_bookings.count()
        pending_bookings = assigned_bookings.filter(status='PENDING').count()
        paid_bookings = assigned_bookings.filter(status='PAID').count()
        
        # Get recent bookings (last 5)
        recent_bookings = assigned_bookings[:5]
        
        # Get upcoming bookings (future travel dates)
        from django.utils import timezone
        upcoming_bookings = assigned_bookings.filter(
            travel_date__gte=timezone.now().date(),
            status='PAID'
        ).order_by('travel_date')
        
        # Get guide reviews and average rating
        guide_reviews = guide.reviews.all().order_by('-id')[:5]
        average_rating = guide.average_rating()
        
        # Calculate total earnings (from paid bookings)
        from django.db.models import Sum
        total_earnings = assigned_bookings.filter(status='PAID').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        context = {
            'guide': guide,
            'assigned_bookings': assigned_bookings,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'paid_bookings': paid_bookings,
            'recent_bookings': recent_bookings,
            'upcoming_bookings': upcoming_bookings,
            'guide_reviews': guide_reviews,
            'average_rating': average_rating,
            'total_earnings': total_earnings,
        }
    else:
        context = {'guide': None}
    
    return render(request, "guide_dashboard.html", context)

@login_required
def admin_dashboard(request):
    # Check if user is admin
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')
    
    # Get database statistics
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # User statistics
    total_users = User.objects.count()
    new_users_this_month = User.objects.filter(
        date_joined__gte=timezone.now().replace(day=1)
    ).count()
    
    # Guide statistics
    total_guides = Guide.objects.count()
    verified_guides = Guide.objects.filter(verified=True).count()
    pending_guides = Guide.objects.filter(verified=False).count()
    
    # Booking statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    paid_bookings = Booking.objects.filter(status='PAID').count()
    failed_bookings = Booking.objects.filter(status='FAILED').count()
    
    # Revenue statistics
    total_revenue = Booking.objects.filter(status='PAID').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    this_month_revenue = Booking.objects.filter(
        status='PAID',
        booking_date__gte=timezone.now().replace(day=1)
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Package statistics
    total_packages = TravelPackage.objects.count()
    total_destinations = Destination.objects.count()
    total_countries = Country.objects.count()
    
    # Recent bookings (last 10)
    recent_bookings = Booking.objects.select_related(
        'user', 'travel_package', 'guide'
    ).order_by('-booking_date')[:10]
    
    # Recent users (last 10)
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Pending guide approvals
    pending_guide_approvals = Guide.objects.filter(verified=False).select_related('user')[:5]
    
    # Contact messages (recent 5)
    recent_contacts = ContactUs.objects.order_by('-created_at')[:5]
    
    context = {
        # User stats
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,
        
        # Guide stats
        'total_guides': total_guides,
        'verified_guides': verified_guides,
        'pending_guides': pending_guides,
        
        # Booking stats
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'paid_bookings': paid_bookings,
        'failed_bookings': failed_bookings,
        
        # Revenue stats
        'total_revenue': total_revenue,
        'this_month_revenue': this_month_revenue,
        
        # Content stats
        'total_packages': total_packages,
        'total_destinations': total_destinations,
        'total_countries': total_countries,
        
        # Recent data
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'pending_guide_approvals': pending_guide_approvals,
        'recent_contacts': recent_contacts,
    }
    
    return render(request, "admin_dashboard.html", context)

@login_required
def guide_profile(request):
    guide = Guide.objects.filter(user=request.user).first()
    return render(request, "guide_profile.html", {"guide": guide})


def request_password_reset(request):
    """
    Handles password reset request.
    Sends an email with password reset link if user email is found.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            current_site = get_current_site(request)
            email_body = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            link = reverse('reset_password_confirm', kwargs={
                'uidb64': email_body['uid'], 'token': email_body['token']})
            reset_url = 'http://' + current_site.domain + link
            email_subject = 'Reset Your Password'
            email_message = EmailMessage(
                email_subject,
                'Hi ' + user.username + ', Click the link below to reset your password of your Expense Tracker Website: \n' + reset_url,
                'noreply@yourdomain.com',
                [email],
            )
            email_message.send(fail_silently=False)
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect("login")
        else:
            messages.error(request, "No account found with this email.")
    return render(request, "reset-password.html")

def reset_password_confirm(request, uidb64, token):
    """
    Confirms password reset using UID and token.
    Allows user to enter new password if token is valid.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if account_activation_token.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                if new_password != confirm_password:
                    messages.error(request, "The passwords do not match. Please try again.")
                    return render(request, 'reset-password-confirm.html', {'validlink': True})
                if len(new_password) < 8:
                    messages.error(request, "Password must be at least 8 characters long.")
                    return render(request, 'reset-password-confirm.html', {'validlink': True})
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully. You can now log in.")
                return redirect('login')
            return render(request, 'reset-password-confirm.html', {'validlink': True})
        else:
            messages.error(request, "The password reset link is invalid.")
            return redirect('login')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
        messages.error(request, "The password reset link is invalid.")
        return redirect('login')
    

# Added
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import generate_token
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from django.utils.encoding import force_bytes, force_str

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request,'activation_failed.html')
    
def verify_code(request):
    if request.method == "POST":
        code = request.POST.get('code')
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('signup')
        user = User.objects.get(id=user_id)
        profile = user.profile
        if profile.email_verification_code == code:
            user.is_active = True
            user.save()
            profile.is_verified = True
            profile.save()
            messages.success(request, "Your account is verified! You can now sign in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid verification code. Try again.")
    return render(request, 'verify_code.html')


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
import random

# Function to generate code
def generate_verification_code():
    return str(random.randint(100000, 999999)) 


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters!")
            return redirect('signup')
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')
        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('signup')

        # Create inactive user
        myuser = User.objects.create_user(username=username, email=email, password=password1)
        myuser.is_active = False
        myuser.save()

        # Generate verification code
        code = generate_verification_code()

        # Save code in Profile
        profile = Profile.objects.create(user=myuser, email_verification_code=code)

        # Send verification code email
        subject = "Your TrekNepal Verification Code"
        message = f"Hello {myuser.first_name},\n\nYour verification code is: {code}\n\nEnter this code on the verification page to activate your account."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [myuser.email], fail_silently=False)

        # Store user id in session for verification
        request.session['user_id'] = myuser.id

        messages.success(request, "Account created! Please check your email for the verification code.")
        return redirect('verify_code')

    return render(request, "signup.html")


# Added

# app/views.py
import requests
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Booking


import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from .models import TravelPackage, Booking
from django.contrib.auth.decorators import login_required

import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from .models import TravelPackage, Booking

@login_required
def khalti_initiate_temp(request):
    booking_data = request.session.get('pending_booking')
    if not booking_data:
        # If session expired or user visits directly
        return redirect('package_list')

    travel_package = get_object_or_404(TravelPackage, id=booking_data["travel_id"])

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "return_url": request.build_absolute_uri("/khalti/verify/"),
        "website_url": request.build_absolute_uri("/"),
        "amount": int(booking_data["total_price"] * 100),  # paisa
        "purchase_order_id": "temp",
        "purchase_order_name": travel_package.title,
    }

    response = requests.post(
        "https://a.khalti.com/api/v2/epayment/initiate/",
        json=payload,
        headers=headers
    )

    result = response.json()

    if "payment_url" in result:
        return redirect(result["payment_url"])
    else:
        # If initiation failed
        return redirect("package_list")

# @login_required
# def khalti_verify(request):
#     pidx = request.GET.get("pidx")
#     if not pidx:
#         return redirect("package_list")

#     headers = {
#         "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }

#     payload = {"pidx": pidx}

#     response = requests.post(
#         "https://a.khalti.com/api/v2/epayment/lookup/",
#         json=payload,
#         headers=headers
#     )

#     result = response.json()
#     print("Khalti verify result:", result)

#     if result.get("status") == "Completed":
#         booking_data = request.session.get('pending_booking')
#         if booking_data:
#             travel_package = get_object_or_404(TravelPackage, id=booking_data["travel_id"])

#             booking = Booking.objects.create(
#                 user=request.user,
#                 travel_package=travel_package,
#                 num_people=booking_data["num_people"],
#                 travel_date=booking_data["travel_date"],
#                 total_price=booking_data["total_price"],
#                 status="PAID",
#                 khalti_pidx=pidx
#             )

#             # Clear pending booking from session
#             del request.session['pending_booking']

#     return redirect("my_bookings")

# @login_required
# def rate_guide(request, booking_id):
#     booking = get_object_or_404(
#         Booking,
#         id=booking_id,
#         user=request.user,
#         guide__isnull=False
#     )

#     if request.method == "POST":
#         GuideReview.objects.create(
#             booking=booking,
#             guide=booking.guide,
#             user=request.user,
#             rating=request.POST["rating"],
#             comment=request.POST.get("comment", "")
#         )
#         return redirect("booking_detail", booking.id)

#     return render(request, "rate_guide.html", {"booking": booking})




# Added today 


from .utils import send_booking_email

@login_required
def khalti_verify(request):
    pidx = request.GET.get("pidx")
    if not pidx:
        return redirect("package_list")

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"pidx": pidx}

    response = requests.post(
        "https://a.khalti.com/api/v2/epayment/lookup/",
        json=payload,
        headers=headers
    )

    result = response.json()
    print("Khalti verify result:", result)

    if result.get("status") == "Completed":
        booking_data = request.session.get('pending_booking')
        if booking_data:
            travel_package = get_object_or_404(
                TravelPackage, id=booking_data["travel_id"]
            )

            booking = Booking.objects.create(
                user=request.user,
                travel_package=travel_package,
                num_people=booking_data["num_people"],
                travel_date=booking_data["travel_date"],
                total_price=booking_data["total_price"],
                status="PAID",
                khalti_pidx=pidx
            )

            # SEND PDF EMAIL
            send_booking_email(booking)

            del request.session['pending_booking']

    return redirect("my_bookings")

