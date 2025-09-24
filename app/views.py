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


# Helper function to check if user is an admin



def home(request):
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

def destination_detail(request, id):
    destination = get_object_or_404(Destination, id=id)
    return render(request, 'destination_detail.html', {'destination': destination})
# Signup View
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Signup successful! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
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
def package_list(request):
    packages = TravelPackage.objects.all()
    return render(request, "packages.html", {"packages": packages})



def booking_detail(request, id):
    booking = get_object_or_404(Booking, id=id)
    return render(request, 'booking_detail.html', {'booking': booking})

@login_required
def book_travel(request, travel_id):
    travel_package = TravelPackage.objects.get(id=travel_id)
    if request.method == "POST":
        num_people = int(request.POST["num_people"])
        total_price = travel_package.price * num_people

        Booking.objects.create(
            user=request.user,
            travel_package=travel_package,
            num_people=num_people,
            total_price=total_price,
            travel_date=request.POST["travel_date"],
        )

        messages.success(request, "Booking successful!")
        return redirect("my_bookings")

    return render(request, "tour_detail.html", {"package": travel_package})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "my_bookings.html", {"bookings": bookings})


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




def contact_us(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactUs.objects.create(
            name=name,
            email=email,
            message=message
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact_us')

    return render(request, 'contact_us.html')


def explore_countries(request):
    countries = Country.objects.all()
    return render(request, 'explore_countries.html', {'countries': countries})

from django.shortcuts import render, get_object_or_404
from .models import Country

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



def tour_detail(request, pk):
    tour = get_object_or_404(TourDetail, pk=pk)
    return render(request, 'tour_detail.html', {'tour': tour})

def trekking_list(request):
    treks = Trekking.objects.filter(is_active=True)
    return render(request, 'trekking_list.html', {'treks': treks})

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


# def weather_view(request):
#     return render(request, "weather.html")

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

# def guide_register(request):
#     if request.method == "POST":
#         form = GuideRegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             guide = form.save(commit=False)
#             guide.is_active = False  # Wait for admin verification
#             guide.save()
#             return redirect("login")  # redirect to user login or success page
#     else:
#         form = GuideRegisterForm()
#     return render(request, "guide_register.html", {"form": form})


# def guide_login(request):
#     if request.method == "POST":
#         form = GuideLoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data["username"]
#             password = form.cleaned_data["password"]
#             user = authenticate(username=username, password=password)
#             if user is not None and hasattr(user, "guide"):
#                 login(request, user)
#                 return redirect("home")  # or guide dashboard
#     else:
#         form = GuideLoginForm()
#     return render(request, "guide_login.html", {"form": form})

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
    return render(request, "guide_dashboard.html", {"guide": guide})

@login_required
def guide_profile(request):
    guide = Guide.objects.filter(user=request.user).first()
    return render(request, "guide_profile.html", {"guide": guide})

