# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),  # Home page
#     path('signup/', views.signup, name='signup'),  # Signup page
#     path('login/', views.login_view, name='login'),  # Login page
#     path('logout/', views.logout_view, name='logout'),  # Logout page
#     path('packages/', views.package_list, name='packages'),  # Travel packages
#     # path('bus/', views.bus_list, name='bus'),  # Bus list page
#     # path('flight/', views.flight_list, name='flight'),  # Flight list page
#     # path('flight/<int:id>/', views.flight_detail, name='flight_detail'),  # Flight detail page
#     path('book_travel/<int:travel_id>/', views.book_travel, name='book_travel'),  # Booking page for a travel package
#     path('my_bookings/', views.my_bookings, name='my_bookings'),  # My bookings page
#     path('user_data/', views.user_data, name='user_data'),  # Admin: User data
#     path('travel_package_detail/<int:travel_id>/', views.travel_package_detail, name='travel_package_detail'),  # Travel package detail
#     path('contact_us/', views.contact_us, name='contact_us'),  # Contact us page
#     path('explore_countries/', views.explore_countries, name='explore_countries'), 
#     path('booking/<int:id>/', views.booking_detail, name='booking_detail'),
#     path('explore_countries/', views.explore_countries, name='explore_countries'),
#     path('explore_countries/<int:id>/', views.explore_country_detail, name='explore_country_detail'),
#     path('travel-package/<int:travel_id>/', views.travel_package_detail, name='travel_package_detail'),
#     path('search/', views.search_view, name='search'),
#     path('tours/', views.tour_list, name='tour_list'),
#     # path('tours/<int:pk>/', views.tour_detail, name='tour_detail'),
#     path('travel-package/<int:travel_id>/', views.travel_package_detail, name='travel_package_detail'),
#     path('trekking/', views.trekking_list, name='trekking_list'),
#     path('trekking/<slug:slug>/', views.trekking_detail, name='trekking_detail'),

#     path('peak-climbing/', views.peak_climbing_list, name='peak_climbing_list'),
#     path('peak-climbing/<slug:slug>/', views.peak_climbing_detail, name='peak_climbing_detail'),

#     path('book-peak-climbing/<slug:slug>/', views.book_peak_climbing, name='book_peak_climbing'),

#     path('destination/<int:id>/', views.destination_detail, name='destination_detail'),

#   # Fixed missing URL
#  # Explore countries page
# ]
from django.urls import path
from django.shortcuts import render

from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Home and Main Pages
    path('', views.home, name='home'),
    path('packages/', views.package_list, name='package_list'),
    path('contact/', views.contact_us, name='contact_us'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Profile and Bookings
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:id>/', views.booking_detail, name='booking_detail'),
    path('booking/confirmation/', lambda request: render(request, 'booking_confirmation.html'), name='booking_confirmation'),
    path('user-data/', views.user_data, name='user_data'),
    
    # Destinations
    path('destination/<int:id>/', views.destination_detail, name='destination_detail'),
    path('countries/', views.explore_countries, name='explore_countries'),
    path('countries/<int:id>/', views.explore_country_detail, name='explore_country_detail'),
    
    # Travel Packages
    path('package/<int:travel_id>/', views.travel_package_detail, name='travel_package_detail'),
    path('book/<int:travel_id>/', views.book_travel, name='book_travel'),
    
    # Tours
    path('tours/', views.tour_list, name='tour_list'),
    path('tour/<int:pk>/', views.tour_detail, name='tour_detail'),
    
    # Trekking
    path('trekking/', views.trekking_list, name='trekking_list'),
    path('trekking/<slug:slug>/', views.trekking_detail, name='trekking_detail'),
    
    # Peak Climbing
    path('peak-climbing/', views.peak_climbing_list, name='peak_climbing_list'),
    path('peak-climbing/<slug:slug>/', views.peak_climbing_detail, name='peak_climbing_detail'),
    path('book-peak-climbing/<slug:slug>/', views.book_peak_climbing, name='book_peak_climbing'),
    
    # Search
    path('search/', views.search_view, name='search_view'),

    path("weather/", views.weather_view, name="weather_view"),

    path("currency-converter/", views.currency_converter, name="currency_converter"),
    path('trek-map/', views.trek_map_view, name='trek_map'),


    # Guide

path("guide/login/", views.guide_login, name="guide_login"),
path("guide/register/", views.guide_register, name="guide_register"),


 # Guide Dashboard
  path("guide/dashboard/", views.guide_dashboard, name="guide_dashboard"),
path("guide/profile/", views.guide_profile, name="guide_profile"),
]