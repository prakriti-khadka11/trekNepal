"""
Custom Package Request System Views
Allows users to request custom travel packages and admins to manage them
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from .models import CustomPackageRequest, RequestQuote, RequestMessage
from .forms import CustomPackageRequestForm, RequestQuoteForm, RequestMessageForm


# Helper function to check if user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff


@login_required
def create_custom_request(request):
    """
    User creates a new custom package request
    """
    if request.method == 'POST':
        form = CustomPackageRequestForm(request.POST, request.FILES)
        if form.is_valid():
            custom_request = form.save(commit=False)
            custom_request.user = request.user
            custom_request.save()
            
            # Send email notification to admin
            try:
                send_mail(
                    subject=f'New Custom Package Request from {request.user.username}',
                    message=f'A new custom package request has been submitted.\n\n'
                            f'Destination: {custom_request.destination}\n'
                            f'Dates: {custom_request.preferred_start_date} to {custom_request.preferred_end_date}\n'
                            f'Travelers: {custom_request.num_travelers}\n'
                            f'Budget: ${custom_request.budget_min} - ${custom_request.budget_max} per person\n\n'
                            f'View details in admin dashboard.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Your custom package request has been submitted successfully! We will review it and get back to you soon.')
            return redirect('my_custom_requests')
    else:
        form = CustomPackageRequestForm()
    
    context = {
        'form': form,
    }
    return render(request, 'custom_requests/create_request.html', context)


@login_required
def my_custom_requests(request):
    """
    User views all their custom package requests
    """
    requests_list = CustomPackageRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Count by status
    status_counts = {
        'pending': requests_list.filter(status='PENDING').count(),
        'reviewing': requests_list.filter(status='REVIEWING').count(),
        'quoted': requests_list.filter(status='QUOTED').count(),
        'accepted': requests_list.filter(status='ACCEPTED').count(),
    }
    
    context = {
        'requests': requests_list,
        'status_counts': status_counts,
    }
    return render(request, 'custom_requests/my_requests.html', context)


@login_required
def view_custom_request(request, request_id):
    """
    User views details of a specific custom request
    """
    custom_request = get_object_or_404(CustomPackageRequest, id=request_id, user=request.user)
    quotes = custom_request.quotes.all().order_by('-created_at')
    messages_list = custom_request.messages.all().order_by('created_at')
    
    # Mark admin messages as read
    custom_request.messages.filter(is_admin_message=True, is_read=False).update(is_read=True)
    
    # Handle new message submission
    if request.method == 'POST':
        message_form = RequestMessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            new_message.custom_request = custom_request
            new_message.sender = request.user
            new_message.is_admin_message = False
            new_message.save()
            
            messages.success(request, 'Message sent successfully!')
            return redirect('view_custom_request', request_id=request_id)
    else:
        message_form = RequestMessageForm()
    
    context = {
        'custom_request': custom_request,
        'quotes': quotes,
        'messages': messages_list,
        'message_form': message_form,
    }
    return render(request, 'custom_requests/view_request.html', context)


@login_required
def accept_quote(request, quote_id):
    """
    User accepts a quote
    """
    quote = get_object_or_404(RequestQuote, id=quote_id, custom_request__user=request.user)
    
    if quote.is_expired():
        messages.error(request, 'This quote has expired. Please request a new quote.')
        return redirect('view_custom_request', request_id=quote.custom_request.id)
    
    if request.method == 'POST':
        quote.accepted = True
        quote.accepted_at = timezone.now()
        quote.save()
        
        # Update request status
        quote.custom_request.status = 'ACCEPTED'
        quote.custom_request.save()
        
        # Send notification email
        try:
            send_mail(
                subject='Quote Accepted - TrekNepal',
                message=f'Great news! {request.user.username} has accepted your quote for {quote.package_title}.\n\n'
                        f'Total Amount: ${quote.total_price}\n'
                        f'Please proceed with booking arrangements.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, 'Quote accepted! Our team will contact you shortly to finalize the booking.')
        return redirect('view_custom_request', request_id=quote.custom_request.id)
    
    context = {
        'quote': quote,
    }
    return render(request, 'custom_requests/accept_quote.html', context)


@login_required
def reject_quote(request, quote_id):
    """
    User rejects a quote
    """
    quote = get_object_or_404(RequestQuote, id=quote_id, custom_request__user=request.user)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Update request status back to reviewing
        quote.custom_request.status = 'REVIEWING'
        quote.custom_request.save()
        
        # Create a message with rejection reason
        if reason:
            RequestMessage.objects.create(
                custom_request=quote.custom_request,
                sender=request.user,
                message=f"Quote rejected. Reason: {reason}",
                is_admin_message=False
            )
        
        messages.info(request, 'Quote rejected. We will work on a revised quote for you.')
        return redirect('view_custom_request', request_id=quote.custom_request.id)
    
    context = {
        'quote': quote,
    }
    return render(request, 'custom_requests/reject_quote.html', context)


# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_custom_requests(request):
    """
    Admin dashboard for managing custom package requests
    """
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    requests_list = CustomPackageRequest.objects.all().select_related('user')
    
    # Apply filters
    if status_filter:
        requests_list = requests_list.filter(status=status_filter)
    
    if search_query:
        requests_list = requests_list.filter(
            Q(destination__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Order by priority and date
    requests_list = requests_list.order_by('-priority', '-created_at')
    
    # Statistics
    stats = {
        'total': CustomPackageRequest.objects.count(),
        'pending': CustomPackageRequest.objects.filter(status='PENDING').count(),
        'reviewing': CustomPackageRequest.objects.filter(status='REVIEWING').count(),
        'quoted': CustomPackageRequest.objects.filter(status='QUOTED').count(),
        'accepted': CustomPackageRequest.objects.filter(status='ACCEPTED').count(),
        'converted': CustomPackageRequest.objects.filter(status='CONVERTED').count(),
    }
    
    context = {
        'requests': requests_list,
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'custom_requests/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_view_request(request, request_id):
    """
    Admin views and manages a specific custom request
    """
    custom_request = get_object_or_404(CustomPackageRequest, id=request_id)
    quotes = custom_request.quotes.all().order_by('-created_at')
    messages_list = custom_request.messages.all().order_by('created_at')
    
    # Mark user messages as read
    custom_request.messages.filter(is_admin_message=False, is_read=False).update(is_read=True)
    
    # Handle status update
    if request.method == 'POST' and 'update_status' in request.POST:
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        custom_request.status = new_status
        if admin_notes:
            custom_request.admin_notes = admin_notes
        custom_request.reviewed_at = timezone.now()
        custom_request.save()
        
        messages.success(request, 'Request status updated successfully!')
        return redirect('admin_view_request', request_id=request_id)
    
    # Handle new message
    if request.method == 'POST' and 'send_message' in request.POST:
        message_form = RequestMessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            new_message.custom_request = custom_request
            new_message.sender = request.user
            new_message.is_admin_message = True
            new_message.save()
            
            messages.success(request, 'Message sent to user!')
            return redirect('admin_view_request', request_id=request_id)
    else:
        message_form = RequestMessageForm()
    
    context = {
        'custom_request': custom_request,
        'quotes': quotes,
        'messages': messages_list,
        'message_form': message_form,
    }
    return render(request, 'custom_requests/admin_view_request.html', context)


@login_required
@user_passes_test(is_admin)
def admin_create_quote(request, request_id):
    """
    Admin creates a quote for a custom request
    """
    custom_request = get_object_or_404(CustomPackageRequest, id=request_id)
    
    if request.method == 'POST':
        form = RequestQuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.custom_request = custom_request
            
            # Calculate expiry date
            quote.expires_at = timezone.now() + timedelta(days=quote.validity_days)
            quote.save()
            
            # Update request status
            custom_request.status = 'QUOTED'
            custom_request.save()
            
            # Send email to user
            try:
                send_mail(
                    subject='New Quote for Your Custom Package Request - TrekNepal',
                    message=f'Good news! We have prepared a quote for your custom package request.\n\n'
                            f'Package: {quote.package_title}\n'
                            f'Price: ${quote.total_price} for {custom_request.num_travelers} travelers\n'
                            f'Valid until: {quote.expires_at.strftime("%Y-%m-%d")}\n\n'
                            f'Please login to view the complete quote and accept it.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[custom_request.user.email],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Quote created and sent to user successfully!')
            return redirect('admin_view_request', request_id=request_id)
    else:
        # Pre-fill form with request data
        initial_data = {
            'price_per_person': (custom_request.budget_min + custom_request.budget_max) / 2,
            'total_price': ((custom_request.budget_min + custom_request.budget_max) / 2) * custom_request.num_travelers,
        }
        form = RequestQuoteForm(initial=initial_data)
    
    context = {
        'form': form,
        'custom_request': custom_request,
    }
    return render(request, 'custom_requests/admin_create_quote.html', context)
