"""
Guide Rating and Review System
Allows travelers to rate guides after travel completion
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Booking, Guide, GuideReview
from .forms import GuideReviewForm


@login_required
def rate_guide(request, booking_id):
    """
    Allow user to rate and review their guide after travel completion
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if booking has a guide assigned
    if not booking.guide:
        messages.error(request, "No guide was assigned to this booking.")
        return redirect('my_bookings')
    
    # Check if travel date has passed
    if booking.travel_date > timezone.now().date():
        messages.warning(request, "You can only rate the guide after your travel is completed.")
        return redirect('my_bookings')
    
    # Check if already reviewed
    if hasattr(booking, 'guidereview'):
        messages.info(request, "You have already reviewed this guide.")
        return redirect('view_guide_review', booking_id=booking_id)
    
    if request.method == 'POST':
        form = GuideReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.guide = booking.guide
            review.user = request.user
            review.save()
            
            # Update booking guide_rating field
            booking.guide_rating = review.rating
            booking.save()
            
            messages.success(request, f"Thank you for rating {booking.guide.user.get_full_name() or booking.guide.user.username}!")
            return redirect('my_bookings')
    else:
        form = GuideReviewForm()
    
    context = {
        'booking': booking,
        'guide': booking.guide,
        'form': form,
    }
    return render(request, 'guide_rating/rate_guide.html', context)


@login_required
def view_guide_review(request, booking_id):
    """
    View the review that user has already submitted
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not hasattr(booking, 'guidereview'):
        messages.error(request, "No review found for this booking.")
        return redirect('my_bookings')
    
    context = {
        'booking': booking,
        'review': booking.guidereview,
        'guide': booking.guide,
    }
    return render(request, 'guide_rating/view_review.html', context)


@login_required
def guide_profile_public(request, guide_id):
    """
    Public profile view for a guide showing their ratings and reviews
    """
    guide = get_object_or_404(Guide, id=guide_id)
    
    # Get all reviews for this guide
    reviews = GuideReview.objects.filter(guide=guide).select_related('user', 'booking').order_by('-created_at')
    
    # Calculate statistics
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Rating distribution
    rating_distribution = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }
    
    # Calculate percentages
    total = stats['total_reviews'] or 1
    rating_percentages = {
        rating: (count / total * 100) for rating, count in rating_distribution.items()
    }
    
    # Determine guide level
    guide_level = get_guide_level(stats['average_rating'], stats['total_reviews'])
    
    context = {
        'guide': guide,
        'reviews': reviews,
        'average_rating': stats['average_rating'] or 0,
        'total_reviews': stats['total_reviews'],
        'rating_distribution': rating_distribution,
        'rating_percentages': rating_percentages,
        'guide_level': guide_level,
    }
    return render(request, 'guide_rating/guide_profile_public.html', context)


def get_guide_level(average_rating, total_reviews):
    """
    Determine guide level based on average rating and number of reviews
    Returns: dict with level name, badge color, and description
    """
    if not average_rating or total_reviews == 0:
        return {
            'name': 'New Guide',
            'badge': 'secondary',
            'description': 'Just starting their journey',
            'icon': '🌱'
        }
    
    # Need minimum reviews to qualify for higher levels
    if total_reviews < 5:
        return {
            'name': 'Beginner',
            'badge': 'info',
            'description': 'Building experience',
            'icon': '⭐'
        }
    
    # Level determination based on rating and experience
    if average_rating >= 4.8 and total_reviews >= 50:
        return {
            'name': 'Elite Guide',
            'badge': 'danger',
            'description': 'Exceptional service with extensive experience',
            'icon': '👑'
        }
    elif average_rating >= 4.5 and total_reviews >= 30:
        return {
            'name': 'Expert Guide',
            'badge': 'warning',
            'description': 'Highly experienced and trusted',
            'icon': '🏆'
        }
    elif average_rating >= 4.0 and total_reviews >= 15:
        return {
            'name': 'Professional Guide',
            'badge': 'success',
            'description': 'Reliable and experienced',
            'icon': '✨'
        }
    elif average_rating >= 3.5 and total_reviews >= 5:
        return {
            'name': 'Intermediate Guide',
            'badge': 'primary',
            'description': 'Growing expertise',
            'icon': '⭐'
        }
    else:
        return {
            'name': 'Developing Guide',
            'badge': 'secondary',
            'description': 'Working to improve',
            'icon': '📈'
        }


@login_required
def all_guides_list(request):
    """
    List all verified guides with their ratings for travelers to browse
    """
    guides = Guide.objects.filter(verified=True).select_related('user')
    
    # Add rating info to each guide
    guides_with_ratings = []
    for guide in guides:
        reviews = GuideReview.objects.filter(guide=guide)
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        guide_data = {
            'guide': guide,
            'average_rating': stats['average_rating'] or 0,
            'total_reviews': stats['total_reviews'],
            'guide_level': get_guide_level(stats['average_rating'], stats['total_reviews'])
        }
        guides_with_ratings.append(guide_data)
    
    # Sort by rating (highest first)
    guides_with_ratings.sort(key=lambda x: x['average_rating'], reverse=True)
    
    context = {
        'guides_with_ratings': guides_with_ratings,
    }
    return render(request, 'guide_rating/all_guides_list.html', context)
