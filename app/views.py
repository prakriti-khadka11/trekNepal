from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import TravelPackage, Booking,Review,ContactUs,SliderImage,Country,TourDetail,Trekking,PeakClimbing,PopularPlace,Destination,PeakClimbingBooking,Guide,GuideReview
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
from django.shortcuts import render
from .models import TravelPackage
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ContactUs
from django.conf import settings
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
from .utils import send_booking_email
import requests
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Booking
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from .models import TravelPackage, Booking
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from .models import TravelPackage, Booking
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Guide
from .forms import GuideRegisterForm, GuideLoginForm

from django.contrib import messages

settings.KHALTI_SECRET_KEY
settings.KHALTI_PUBLIC_KEY

# Helper function to check if user is an admin
def home(request):
    """Render the home page. Redirects admin to admin dashboard and verified guides to guide dashboard."""
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

# Login View
def login_view(request):
    """Authenticate user credentials. Redirects guides to guide login, regular users to home."""
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

def signup(request):
    """Register a new user, create an inactive account, and send a 6-digit email verification code."""
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

def verify_code(request):
    """Verify the 6-digit email verification code and activate the user account."""
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

# Function to generate code
def generate_verification_code():
    """Generate a random 6-digit numeric verification code for email confirmation."""
    return str(random.randint(100000, 999999)) 

# Logout View
def logout_view(request):
    """Destroy the user session and redirect to home."""
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")

@login_required(login_url='login')
def package_list(request):
    """List all available travel packages with filtering and search."""
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

@login_required(login_url='login')
def destination_detail(request, id):
    """Display details of a specific destination including gallery images."""
    destination = get_object_or_404(Destination, id=id)
    return render(request, 'destination_detail.html', {'destination': destination})

def booking_detail(request, id):
    """Display full details of a specific booking including itinerary."""
    booking = get_object_or_404(Booking, id=id)
    
    # Check if user is a guide
    if hasattr(request.user, 'guide'):
        return render(request, 'guide_booking_detail.html', {'booking': booking})
    else:
        return render(request, 'booking_detail.html', {'booking': booking})

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def cancel_booking(request, booking_id):
    """Cancel (delete) a booking owned by the current user."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        booking.delete()  # or booking.status = "cancelled"; booking.save()
        messages.success(request, "Your booking has been cancelled.")
        return redirect("my_bookings")
    return redirect("my_bookings")


# Khalti Payment for Trekking
@login_required
def khalti_initiate_trekking(request):
    """Initiate Khalti payment for a trekking booking stored in session."""
    booking_data = request.session.get('pending_trekking_booking')
    if not booking_data:
        return redirect('trekking_list')

    trek = get_object_or_404(Trekking, slug=booking_data["trek_slug"])

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Khalti test mode cap: max Rs.1000 (100000 paisa)
    raw_paisa = int(booking_data["total_price"] * 100)
    amount_paisa = min(raw_paisa, 100000) if settings.DEBUG else raw_paisa

    payload = {
        "return_url": request.build_absolute_uri("/khalti/verify/trekking/"),
        "website_url": request.build_absolute_uri("/"),
        "amount": amount_paisa,
        "purchase_order_id": f"trek_{trek.id}",
        "purchase_order_name": trek.title,
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
        return redirect("trekking_list")

@login_required
def khalti_verify_trekking(request):
    """Verify Khalti payment for trekking, create Booking record, and send confirmation email."""
    pidx = request.GET.get("pidx")
    if not pidx:
        return redirect("trekking_list")

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
    print("Khalti verify trekking result:", result)

    if result.get("status") == "Completed":
        booking_data = request.session.get('pending_trekking_booking')
        if booking_data:
            trek = get_object_or_404(Trekking, slug=booking_data["trek_slug"])

            booking = Booking.objects.create(
                user=request.user,
                travel_package=None,
                trekking=trek,
                trek_date=booking_data["trek_date"],
                num_people=booking_data["num_people"],
                travel_date=booking_data["trek_date"],
                total_price=booking_data["total_price"],
                status="PAID",
                khalti_pidx=pidx,
            )

            # Send confirmation email (safe for trek bookings)
            try:
                send_booking_email(booking)
            except Exception:
                pass  # Don't block redirect if email fails

            messages.success(request, f"Trekking booking for {trek.title} confirmed!")
            del request.session['pending_trekking_booking']

    return redirect("my_bookings")


# Khalti Payment for Peak Climbing
@login_required
def khalti_initiate_peak(request):
    """Initiate Khalti payment for a peak climbing booking stored in session."""
    booking_data = request.session.get('pending_peak_booking')
    if not booking_data:
        return redirect('peak_climbing_list')

    peak = get_object_or_404(PeakClimbing, slug=booking_data["peak_slug"])

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Khalti test mode cap: max Rs.1000 (100000 paisa)
    raw_paisa = int(booking_data["total_price"] * 100)
    amount_paisa = min(raw_paisa, 100000) if settings.DEBUG else raw_paisa

    payload = {
        "return_url": request.build_absolute_uri("/khalti/verify/peak/"),
        "website_url": request.build_absolute_uri("/"),
        "amount": amount_paisa,
        "purchase_order_id": f"peak_{peak.id}",
        "purchase_order_name": peak.title,
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
        return redirect("peak_climbing_list")


@login_required
def khalti_verify_peak(request):
    """Verify Khalti payment for peak climbing and create PeakClimbingBooking record."""
    pidx = request.GET.get("pidx")
    if not pidx:
        return redirect("peak_climbing_list")

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
    print("Khalti verify peak result:", result)

    if result.get("status") == "Completed":
        booking_data = request.session.get('pending_peak_booking')
        if booking_data:
            peak = get_object_or_404(PeakClimbing, slug=booking_data["peak_slug"])
            
            # Create peak climbing booking
            PeakClimbingBooking.objects.create(
                user=request.user,
                peak_climbing=peak,
                num_people=booking_data["num_people"],
                climbing_date=booking_data["climbing_date"],
                total_price=booking_data["total_price"],
            )
            
            messages.success(request, f"Peak climbing booking for {peak.title} confirmed! Payment successful.")
            
            # Clear session
            del request.session['pending_peak_booking']

    return redirect("my_bookings")


@login_required
def khalti_initiate_temp(request):
    """Initiate Khalti payment for a travel package booking stored in session."""
    booking_data = request.session.get('pending_booking')
    if not booking_data:
        # If session expired or user visits directly
        return redirect('package_list')

    travel_package = get_object_or_404(TravelPackage, id=booking_data["travel_id"])

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Khalti test mode cap: max Rs.1000 (100000 paisa)
    raw_paisa = int(booking_data["total_price"] * 100)
    amount_paisa = min(raw_paisa, 100000) if settings.DEBUG else raw_paisa

    payload = {
        "return_url": request.build_absolute_uri("/khalti/verify/"),
        "website_url": request.build_absolute_uri("/"),
        "amount": amount_paisa,
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

@login_required
def khalti_verify(request):
    """Verify Khalti payment for a travel package, create Booking record, and send PDF email."""
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


# Edit profile
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

@login_required
def edit_profile(request):
    """Allow logged-in user to update their first name, last name, and email."""
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
    """Store travel package booking data in session and redirect to Khalti payment."""
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
            "total_price": float(total_price),  
        }

        # Redirect to Khalti payment
        return redirect("khalti_initiate_temp")

    return render(request, "tour_detail.html", {"travel_package": travel_package})


@login_required
def my_bookings(request):
    """Display all bookings for the logged-in user with unread guide message counts."""
    from .models import GuideMessage
    
    bookings = Booking.objects.filter(user=request.user)
    
    # Get unread message count for each booking
    unread_counts = {}
    for booking in bookings:
        if booking.guide and booking.status == 'PAID':
            count = GuideMessage.objects.filter(
                booking=booking,
                is_read=False
            ).exclude(sender=request.user).count()
            unread_counts[booking.id] = count
    
    return render(request, "my_bookings.html", {
        "bookings": bookings,
        "unread_counts": unread_counts
    })

@login_required
def booking_receipt(request, booking_id):
    """Display the HTML booking receipt with dynamic details from the database."""
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
        'package_title': booking.travel_package.title if booking.travel_package else (booking.trekking.title if booking.trekking else f'Booking #{booking.id}'),
        'destination': (
            f"{dynamic_details['destination_info']['name']}, {dynamic_details['destination_info']['location']}"
            if booking.travel_package else
            f"{booking.trekking.title}, {booking.trekking.country}" if booking.trekking else 'N/A'
        ),
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
    """Return all users — used for admin data inspection."""
    users = User.objects.all()
    return render(request, "user_data.html", {"users": users})


@login_required
def travel_package_detail(request, travel_id):
    """Display full details of a travel package including reviews and booking form."""
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


def contact_us(request):
    """Handle contact form submission and save message to database."""
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
    """List all countries/districts available for exploration."""
    countries = Country.objects.all()
    return render(request, 'explore_countries.html', {'countries': countries})

from django.shortcuts import render, get_object_or_404
from .models import Country

# @login_required(login_url='login')
def explore_country_detail(request, id):
    """Display details and destinations for a specific country/district."""
    country = get_object_or_404(Country, id=id)
    return render(request, 'explore_country_detail.html', {'country': country})


def search_view(request):
    """Search across packages, trekking, peak climbing, and destinations by keyword."""
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
    """List all available tour packages."""
    tours = TourDetail.objects.all()
    return render(request, 'tour_list.html', {'tours': tours})


@login_required(login_url='login')
def tour_detail(request, pk):
    """Display details of a specific tour package."""
    tour = get_object_or_404(TourDetail, pk=pk)
    return render(request, 'tour_detail.html', {'tour': tour})

def trekking_list(request):
    """List all active trekking routes."""
    treks = Trekking.objects.filter(is_active=True)
    return render(request, 'trekking_list.html', {'treks': treks})

@login_required(login_url='login')
def trekking_detail(request, slug):
    """Display trekking route details and handle booking form submission."""
    trek = get_object_or_404(Trekking, slug=slug)
    images = trek.gallery_images.all()
    
    if request.method == "POST":
        num_people = int(request.POST["num_people"])
        trek_date = request.POST["trek_date"]
        total_price = trek.price * num_people
        
        # Store booking data in session temporarily
        request.session['pending_trekking_booking'] = {
            "trek_slug": trek.slug,
            "num_people": num_people,
            "trek_date": trek_date,
            "total_price": float(total_price),
        }
        
        # Redirect to Khalti payment
        return redirect("khalti_initiate_trekking")
    
    return render(request, 'trekking_detail.html', {
        'trek': trek,
        'images': images,
    })

def peak_climbing_list(request):
    """List all active peak climbing expeditions."""
    peaks = PeakClimbing.objects.filter(is_active=True)
    return render(request, 'peak_climbing_list.html', {'peaks': peaks})

# Detail view for each Peak Climbing
@login_required(login_url='login')
def peak_climbing_detail(request, slug):
    """Display peak climbing expedition details."""
    peak = get_object_or_404(PeakClimbing, slug=slug)
    return render(request, 'peak_climbing_detail.html', {'peak': peak})

@login_required
def book_peak_climbing(request, slug):
    """Handle peak climbing booking form and store data in session for Khalti payment."""
    peak = get_object_or_404(PeakClimbing, slug=slug)

    if request.method == 'POST':
        num_people = int(request.POST["num_people"])
        climbing_date = request.POST["climbing_date"]
        total_price = peak.price * num_people
        
        # Store booking data in session temporarily
        request.session['pending_peak_booking'] = {
            "peak_slug": peak.slug,
            "num_people": num_people,
            "climbing_date": climbing_date,
            "total_price": float(total_price),
        }
        
        # Redirect to Khalti payment
        return redirect("khalti_initiate_peak")
    
    return render(request, 'book_peak_climbing.html', {'peak': peak})

@login_required
def package_booking(request, package_id):
    package = get_object_or_404(TravelPackage, pk=package_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  
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
    """Render the weather forecast page."""
    return render(request, "weather.html")


def weather_data_api(request):
    """
    Serve weather data from DB cache (30-min refresh).
    Fetches from OpenWeatherMap only if cache is missing or stale.
    Returns JSON with temp, humidity, wind, description, icon.
    """
    import urllib.request, urllib.parse, json
    from django.http import JsonResponse
    from .models import WeatherCache

    city = request.GET.get('city', 'Kathmandu').strip()
    if not city:
        return JsonResponse({'error': 'City required'}, status=400)

    # Check DB cache
    try:
        cached = WeatherCache.objects.get(city__iexact=city)
        if not cached.is_stale():
            return JsonResponse({
                'source': 'cache',
                'city': cached.city,
                'country': cached.country,
                'temp': cached.temp,
                'feels_like': cached.feels_like,
                'humidity': cached.humidity,
                'pressure': cached.pressure,
                'wind_speed': cached.wind_speed,
                'description': cached.description,
                'icon': cached.icon,
                'fetched_at': cached.fetched_at.strftime('%H:%M'),
            })
    except WeatherCache.DoesNotExist:
        cached = None

    # Fetch from OpenWeatherMap
    try:
        api_key = '00d575c13cc87e97c398a87b83d54930'
        url = f'https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(city)}&appid={api_key}&units=metric'
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        if data.get('cod') != 200:
            return JsonResponse({'error': data.get('message', 'City not found')}, status=404)

        w = {
            'city':        data['name'],
            'country':     data['sys'].get('country', ''),
            'temp':        data['main']['temp'],
            'feels_like':  data['main']['feels_like'],
            'humidity':    data['main']['humidity'],
            'pressure':    data['main']['pressure'],
            'wind_speed':  data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'icon':        data['weather'][0]['icon'],
        }

        # Save/update DB cache
        WeatherCache.objects.update_or_create(
            city__iexact=w['city'],
            defaults={**w, 'city': w['city']},
        )

        w['source'] = 'api'
        return JsonResponse(w)

    except Exception as e:
        # If API fails but we have stale cache, return it anyway
        if cached:
            return JsonResponse({
                'source': 'stale_cache',
                'city': cached.city,
                'country': cached.country,
                'temp': cached.temp,
                'feels_like': cached.feels_like,
                'humidity': cached.humidity,
                'pressure': cached.pressure,
                'wind_speed': cached.wind_speed,
                'description': cached.description,
                'icon': cached.icon,
                'fetched_at': cached.fetched_at.strftime('%H:%M'),
            })
        return JsonResponse({'error': 'Weather data unavailable'}, status=503)

@login_required(login_url='login')
def currency_converter(request):
    """Render the currency converter page."""
    return render(request, "currency_converter.html")


def currency_rate_api(request):
    """
    Serve exchange rates from DB cache (6-hour refresh).
    Falls back to live currency API if cache is missing or stale.
    Returns JSON with base currency and all exchange rates.
    """
    import urllib.request, json
    from django.http import JsonResponse
    from .models import CurrencyRate

    base = request.GET.get('base', 'usd').lower().strip()

    # Check DB cache
    try:
        cached = CurrencyRate.objects.get(base_currency=base)
        if not cached.is_stale():
            return JsonResponse({'source': 'cache', 'base': base, 'rates': json.loads(cached.rates_json)})
    except CurrencyRate.DoesNotExist:
        cached = None

    # Fetch from free currency API
    try:
        url = f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json'
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        rates = data.get(base, {})
        rates_str = json.dumps(rates)

        CurrencyRate.objects.update_or_create(
            base_currency=base,
            defaults={'rates_json': rates_str},
        )

        return JsonResponse({'source': 'api', 'base': base, 'rates': rates})

    except Exception as e:
        import traceback
        print("Currency API error:", traceback.format_exc())
        if cached:
            return JsonResponse({'source': 'stale_cache', 'base': base, 'rates': json.loads(cached.rates_json)})
        return JsonResponse({'error': 'Exchange rate data unavailable'}, status=503)


def trek_map_view(request):
    """Render the interactive trek map with route planning and live GPS tracking."""
    return render(request, 'trek_map.html')

 # Guide
def guide_register(request):
    """Handle guide registration — creates both User and Guide records simultaneously."""
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
    """Authenticate guide credentials. Only allows verified guides to access the dashboard."""
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
    """Display guide dashboard with assigned bookings, ratings, and messaging."""
    from .models import GuideMessage
    
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
        
        # Import guide level function
        from .guide_rating_views import get_guide_level
        from django.db.models import Count
        
        # Get guide level based on ratings
        total_reviews = guide.reviews.count()
        guide_level = get_guide_level(average_rating, total_reviews)
        
        # Get unread message count for each booking
        unread_counts = {}
        for booking in assigned_bookings:
            if booking.status == 'PAID':
                count = GuideMessage.objects.filter(
                    booking=booking,
                    is_read=False
                ).exclude(sender=request.user).count()
                unread_counts[booking.id] = count
        
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
            'total_reviews': total_reviews,
            'guide_level': guide_level,
            'unread_counts': unread_counts,
        }
    else:
        context = {'guide': None}
    
    return render(request, "guide_dashboard.html", context)

@login_required
def admin_dashboard(request):
    """Display admin dashboard with statistics, recent bookings, guide approvals, and custom requests."""
    # Check if user is admin
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')
    
    # Get database statistics
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # User statistics
    total_users = User.objects.count()
    new_users_this_month = User.objects.filter(
        date_joined__gte=timezone.now().replace(day=1)
    ).count()
    
    # Guide statistics with ratings
    from .guide_rating_views import get_guide_level
    total_guides = Guide.objects.count()
    verified_guides = Guide.objects.filter(verified=True).count()
    pending_guides = Guide.objects.filter(verified=False).count()
    
    # Get top rated guides
    guides_with_ratings = []
    for guide in Guide.objects.filter(verified=True)[:10]:
        reviews = GuideReview.objects.filter(guide=guide)
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        guide_level = get_guide_level(stats['average_rating'], stats['total_reviews'])
        guides_with_ratings.append({
            'guide': guide,
            'average_rating': stats['average_rating'] or 0,
            'total_reviews': stats['total_reviews'],
            'guide_level': guide_level
        })
    
    # Sort by rating
    guides_with_ratings.sort(key=lambda x: x['average_rating'], reverse=True)
    top_guides = guides_with_ratings[:5]
    
    # Booking statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    paid_bookings = Booking.objects.filter(status='PAID').count()
    failed_bookings = Booking.objects.filter(status='FAILED').count()
    
    # Revenue statistics — bookings + paid custom requests
    booking_revenue = Booking.objects.filter(status='PAID').aggregate(
        total=Sum('total_price')
    )['total'] or 0

    from .models import RequestQuote
    custom_revenue = RequestQuote.objects.filter(accepted=True).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    total_revenue = booking_revenue + custom_revenue

    booking_month_revenue = Booking.objects.filter(
        status='PAID',
        booking_date__gte=timezone.now().replace(day=1)
    ).aggregate(total=Sum('total_price'))['total'] or 0

    custom_month_revenue = RequestQuote.objects.filter(
        accepted=True,
        accepted_at__gte=timezone.now().replace(day=1)
    ).aggregate(total=Sum('total_price'))['total'] or 0

    this_month_revenue = booking_month_revenue + custom_month_revenue
    
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
    
    # Total reviews
    total_reviews = GuideReview.objects.count()
    
    # Custom package requests
    from .models import CustomPackageRequest
    custom_requests = CustomPackageRequest.objects.select_related('user').order_by('-created_at')
    custom_request_stats = {
        'total':     custom_requests.count(),
        'pending':   custom_requests.filter(status='PENDING').count(),
        'reviewing': custom_requests.filter(status='REVIEWING').count(),
        'quoted':    custom_requests.filter(status='QUOTED').count(),
        'accepted':  custom_requests.filter(status='ACCEPTED').count(),
    }
    recent_custom_requests = custom_requests[:8]

    context = {
        # User stats
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,

        # Guide stats
        'total_guides': total_guides,
        'verified_guides': verified_guides,
        'pending_guides': pending_guides,
        'top_guides': top_guides,

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
        'total_reviews': total_reviews,

        # Recent data
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'pending_guide_approvals': pending_guide_approvals,
        'recent_contacts': recent_contacts,

        # Custom requests
        'custom_request_stats': custom_request_stats,
        'recent_custom_requests': recent_custom_requests,
    }
    
    return render(request, "admin_dashboard.html", context)

@login_required
def guide_profile(request):
    """Display the profile page for the logged-in guide."""
    guide = Guide.objects.filter(user=request.user).first()
    return render(request, "guide_profile.html", {"guide": guide})


def request_password_reset(request):
    """Send a password reset link to the user's email using a secure token."""
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
    """Validate the password reset token and allow the user to set a new password."""
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

def activate(request, uidb64, token):
    """Activate user account via email link (legacy activation method)."""
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


#  Packing List Generator 

def _infer_trek_meta(pkg):
    """Infer trek_type (easy/moderate/high_altitude/peak_climbing) and accommodation from package title and destination."""
    title_low = pkg.title.lower()
    location  = (pkg.destination.location or '').lower() if pkg.destination else ''
    dest_name = (pkg.destination.name or '').lower() if pkg.destination else ''
    combined  = title_low + ' ' + location + ' ' + dest_name

    if any(w in combined for w in ['peak','climbing','summit','everest','lhotse','ama dablam','nuptse']):
        trek_type = 'peak_climbing'
    elif any(w in combined for w in ['high altitude','ebc','base camp','manaslu','kanchenjunga','dolpo','makalu']):
        trek_type = 'high_altitude'
    elif any(w in combined for w in ['moderate','annapurna','langtang','circuit','ghandruk','ghorepani','poon hill']):
        trek_type = 'moderate'
    else:
        trek_type = 'easy'

    accommodation = 'camping' if any(w in title_low for w in ['camping','camp','expedition']) else 'teahouse'
    return trek_type, accommodation


def _infer_season(travel_date):
    """Determine trekking season (spring/monsoon/autumn/winter) from the travel date month."""
    m = travel_date.month
    if m in [3, 4, 5]:   return 'spring'
    if m in [6, 7, 8]:   return 'monsoon'
    if m in [9, 10, 11]: return 'autumn'
    return 'winter'


@login_required(login_url='login')
def packing_list(request):
    """
    Packing List Generator — user selects a trip and season,
    items are fetched from PackingTemplate DB table and displayed by category.
    """
    from .models import PackingTemplate, TravelPackage, Trekking, PeakClimbing

    # All available trips for the selector
    packages = TravelPackage.objects.all().select_related('destination')
    treks    = Trekking.objects.filter(is_active=True)
    peaks    = PeakClimbing.objects.filter(is_active=True)

    SEASONS = [
        ('spring',  'Spring (Mar–May)'),
        ('monsoon', 'Monsoon (Jun–Aug)'),
        ('autumn',  'Autumn (Sep–Nov)'),
        ('winter',  'Winter (Dec–Feb)'),
    ]

    result = None

    if request.method == 'POST':
        trip_type_key = request.POST.get('trip_type_key')   # e.g. 'package_4', 'trek_2', 'peak_1'
        season        = request.POST.get('season', 'autumn')
        num_people    = int(request.POST.get('num_people', 1) or 1)

        # Resolve trip name and trek_type from the key
        trip_name = ''
        trek_type = 'easy'
        duration  = 7

        if trip_type_key:
            kind, pk = trip_type_key.split('_', 1)
            pk = int(pk)
            if kind == 'package':
                obj = TravelPackage.objects.select_related('destination').get(pk=pk)
                trip_name = obj.title
                duration  = obj.duration or 7
                trek_type, _ = _infer_trek_meta(obj)
            elif kind == 'trek':
                obj = Trekking.objects.get(pk=pk)
                trip_name = obj.title
                try:
                    duration = int(obj.duration.split()[0])
                except Exception:
                    duration = 14
                diff = obj.difficulty.lower()
                title = obj.title.lower()
                if any(w in title or w in diff for w in ['challenging','hard','manaslu','dolpo','kanchenjunga','makalu']):
                    trek_type = 'high_altitude'
                elif any(w in title or w in diff for w in ['moderate','annapurna','langtang','circuit','ebc','everest']):
                    trek_type = 'moderate'
                else:
                    trek_type = 'easy'
            elif kind == 'peak':
                obj = PeakClimbing.objects.get(pk=pk)
                trip_name = obj.title
                try:
                    duration = int(obj.duration.split()[0])
                except Exception:
                    duration = 60
                trek_type = 'peak_climbing'

        # Fetch items from PackingTemplate
        templates = PackingTemplate.objects.filter(
            trip_type=trek_type,
            season__in=[season, 'all'],
        ).order_by('category', '-priority', 'name')

        categories = {}
        for t in templates:
            categories.setdefault(t.category, []).append(t)

        result = {
            'trip_name': trip_name,
            'trek_type': trek_type,
            'season': season,
            'num_people': num_people,
            'duration': duration,
            'categories': categories,
            'total_items': templates.count(),
        }

    return render(request, 'packing_list.html', {
        'packages': packages,
        'treks':    treks,
        'peaks':    peaks,
        'seasons':  SEASONS,
        'result':   result,
    })


# --- Trek Fitness Matcher ---
@login_required(login_url='login')
def trek_matcher(request):
    """Render the Trek Fitness Matcher page with all active treks passed for JS scoring."""
    treks = Trekking.objects.filter(is_active=True)
    return render(request, 'trek_matcher.html', {'treks': treks})

