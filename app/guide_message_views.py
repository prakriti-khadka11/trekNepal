from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from .models import Booking, GuideMessage, Guide
from django.db.models import Q, Count, Case, When, IntegerField

def get_unread_message_count(user):
    """Get count of unread messages for a user"""
    if hasattr(user, 'guide'):
        # For guides: count unread messages from travelers in their bookings
        return GuideMessage.objects.filter(
            booking__guide=user.guide,
            is_read=False
        ).exclude(sender=user).count()
    else:
        # For travelers: count unread messages from guides in their bookings
        return GuideMessage.objects.filter(
            booking__user=user,
            is_read=False
        ).exclude(sender=user).count()


def get_unread_count_per_booking(user):
    """Get unread message count for each booking"""
    if hasattr(user, 'guide'):
        # For guides
        bookings = Booking.objects.filter(guide=user.guide, status='PAID')
    else:
        # For travelers
        bookings = Booking.objects.filter(user=user, guide__isnull=False, status='PAID')
    
    unread_counts = {}
    for booking in bookings:
        count = GuideMessage.objects.filter(
            booking=booking,
            is_read=False
        ).exclude(sender=user).count()
        unread_counts[booking.id] = count
    
    return unread_counts


@login_required
def guide_chat(request, booking_id):
    """Chat interface between user and guide for a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is authorized (either the booking user or the assigned guide)
    is_guide = hasattr(request.user, 'guide') and booking.guide == request.user.guide
    is_traveler = booking.user == request.user
    
    if not (is_guide or is_traveler):
        django_messages.error(request, "You don't have permission to view this conversation.")
        return redirect('home')
    
    # Get all messages for this booking
    chat_messages = GuideMessage.objects.filter(booking=booking)
    
    # Mark messages as read if they're not from the current user
    chat_messages.exclude(sender=request.user).update(is_read=True)
    
    # Determine the other party in the conversation
    if is_guide:
        other_party = booking.user
        other_party_role = "Traveler"
    else:
        other_party = booking.guide.user if booking.guide else None
        other_party_role = "Guide"
    
    context = {
        'booking': booking,
        'chat_messages': chat_messages,
        'other_party': other_party,
        'other_party_role': other_party_role,
        'is_guide': is_guide,
    }
    
    return render(request, 'guide_messages/chat.html', context)


@login_required
def send_message(request, booking_id):
    """Send a message in the guide-user chat"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check authorization
        is_guide = hasattr(request.user, 'guide') and booking.guide == request.user.guide
        is_traveler = booking.user == request.user
        
        if not (is_guide or is_traveler):
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        message_text = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')
        
        if message_text or attachment:
            GuideMessage.objects.create(
                booking=booking,
                sender=request.user,
                message=message_text,
                attachment=attachment
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                django_messages.success(request, "Message sent successfully!")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
            else:
                django_messages.error(request, "Message cannot be empty.")
        
        return redirect('guide_chat', booking_id=booking_id)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
