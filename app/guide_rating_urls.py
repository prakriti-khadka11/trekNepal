"""
URL patterns for Guide Rating and Review System
"""
from django.urls import path
from . import guide_rating_views

urlpatterns = [
    # Rate guide after travel
    path('rate/<int:booking_id>/', guide_rating_views.rate_guide, name='rate_guide'),
    
    # View submitted review
    path('review/<int:booking_id>/', guide_rating_views.view_guide_review, name='view_guide_review'),
    
    # Public guide profile with ratings
    path('guide/<int:guide_id>/profile/', guide_rating_views.guide_profile_public, name='guide_profile_public'),
    
    # List all guides with ratings
    path('guides/', guide_rating_views.all_guides_list, name='all_guides_list'),
]
