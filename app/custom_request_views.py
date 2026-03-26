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
    
    status_counts = {
        'pending':  requests_list.filter(status='PENDING').count(),
        'accepted': requests_list.filter(status='ACCEPTED').count(),
        'rejected': requests_list.filter(status='REJECTED').count(),
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
    """User accepts a quote — immediately redirects to Khalti payment."""
    quote = get_object_or_404(RequestQuote, id=quote_id, custom_request__user=request.user)

    if quote.is_expired():
        messages.error(request, 'This quote has expired. Please request a new quote.')
        return redirect('view_custom_request', request_id=quote.custom_request.id)

    if quote.custom_request.status == 'ACCEPTED':
        messages.info(request, 'This request is already accepted and paid.')
        return redirect('view_custom_request', request_id=quote.custom_request.id)

    if request.method == 'POST':
        # Store quote id in session and go to Khalti
        request.session['pending_custom_quote_id'] = quote.id
        return redirect('khalti_initiate_custom', quote_id=quote.id)

    return render(request, 'custom_requests/accept_quote.html', {'quote': quote})


@login_required
def khalti_initiate_custom(request, quote_id):
    """Initiate Khalti payment for a custom package quote."""
    import requests as req
    quote = get_object_or_404(RequestQuote, id=quote_id, custom_request__user=request.user)

    raw_paisa = int(float(quote.total_price) * 100)
    amount_paisa = min(raw_paisa, 100000) if settings.DEBUG else raw_paisa

    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'return_url': request.build_absolute_uri('/custom-request/khalti/verify/'),
        'website_url': request.build_absolute_uri('/'),
        'amount': amount_paisa,
        'purchase_order_id': f'custom_{quote.id}',
        'purchase_order_name': quote.package_title,
    }
    response = req.post('https://a.khalti.com/api/v2/epayment/initiate/', json=payload, headers=headers)
    result = response.json()

    if 'payment_url' in result:
        request.session['pending_custom_quote_id'] = quote.id
        return redirect(result['payment_url'])

    messages.error(request, 'Payment initiation failed. Please try again.')
    return redirect('view_custom_request', request_id=quote.custom_request.id)


@login_required
def khalti_verify_custom(request):
    """Verify Khalti payment for custom package and lock the request."""
    import requests as req
    pidx = request.GET.get('pidx')
    if not pidx:
        return redirect('my_custom_requests')

    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    response = req.post('https://a.khalti.com/api/v2/epayment/lookup/', json={'pidx': pidx}, headers=headers)
    result = response.json()

    if result.get('status') == 'Completed':
        quote_id = request.session.get('pending_custom_quote_id')
        if quote_id:
            quote = get_object_or_404(RequestQuote, id=quote_id, custom_request__user=request.user)
            quote.accepted = True
            quote.accepted_at = timezone.now()
            quote.save()
            # Auto-set status to ACCEPTED and lock it
            cr = quote.custom_request
            cr.status = 'ACCEPTED'
            cr.admin_notes = (cr.admin_notes or '') + f'\n[PAID] Khalti pidx: {pidx}'
            cr.save()
            request.session.pop('pending_custom_quote_id', None)
            messages.success(request, 'Payment successful! Your custom package is confirmed.')

    return redirect('my_custom_requests')


@login_required
def reject_quote(request, quote_id):
    """User rejects a quote — allows admin to re-quote if travel date > 7 days away."""
    quote = get_object_or_404(RequestQuote, id=quote_id, custom_request__user=request.user)
    cr = quote.custom_request

    # Check if travel date is more than 7 days away
    from datetime import date
    days_until_travel = (cr.preferred_start_date - date.today()).days
    can_renegotiate = days_until_travel > 7

    if request.method == 'POST':
        if not can_renegotiate:
            messages.error(request, 'Cannot reject the quote — travel date is within 7 days. Please accept or contact us.')
            return redirect('view_custom_request', request_id=cr.id)

        reason = request.POST.get('reason', '')
        # Set back to PENDING so admin can create a new quote
        cr.status = 'PENDING'
        cr.save()

        if reason:
            RequestMessage.objects.create(
                custom_request=cr,
                sender=request.user,
                message=f"Quote rejected. Reason: {reason}",
                is_admin_message=False
            )

        messages.info(request, 'Quote rejected. The admin can now send a revised quote.')
        return redirect('view_custom_request', request_id=cr.id)

    return render(request, 'custom_requests/reject_quote.html', {
        'quote': quote,
        'can_renegotiate': can_renegotiate,
        'days_until_travel': days_until_travel,
    })


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

        # Once ACCEPTED (paid), nobody can change the status
        if custom_request.status == 'ACCEPTED':
            messages.error(request, 'This request is already accepted and paid. Status cannot be changed.')
            return redirect('admin_view_request', request_id=request_id)

        # Once REJECTED by admin, it stays rejected — no going back
        if custom_request.status == 'REJECTED':
            messages.error(request, 'This request has been rejected and cannot be changed.')
            return redirect('admin_view_request', request_id=request_id)

        # Admin cannot manually set Accepted
        if new_status == 'ACCEPTED':
            messages.error(request, 'Accepted status is set automatically after the user pays.')
            return redirect('admin_view_request', request_id=request_id)

        # Admin cannot set back to PENDING once rejected
        if new_status == 'PENDING' and custom_request.status == 'REJECTED':
            messages.error(request, 'A rejected request cannot be set back to Pending.')
            return redirect('admin_view_request', request_id=request_id)

        custom_request.status = new_status
        if admin_notes:
            custom_request.admin_notes = admin_notes
        custom_request.reviewed_at = timezone.now()
        custom_request.save()

        messages.success(request, 'Status updated.')
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
    """Admin creates a quote — only for PENDING requests."""
    custom_request = get_object_or_404(CustomPackageRequest, id=request_id)

    if custom_request.status not in ('PENDING',):
        messages.error(request, 'Can only create a quote for a pending request.')
        return redirect('admin_view_request', request_id=request_id)
    
    if request.method == 'POST':
        form = RequestQuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.custom_request = custom_request
            quote.expires_at = timezone.now() + timedelta(days=quote.validity_days)
            quote.save()
            custom_request.status = 'QUOTED'
            custom_request.save()
            try:
                send_mail(
                    subject='New Quote for Your Custom Package Request - TrekNepal',
                    message=(
                        f'Good news! We have prepared a quote for your custom package request.\n\n'
                        f'Package: {quote.package_title}\n'
                        f'Total Price: Rs. {quote.total_price} for {custom_request.num_travelers} travelers\n'
                        f'Valid until: {quote.expires_at.strftime("%Y-%m-%d")}\n\n'
                        f'Please login to view the complete quote and accept it.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[custom_request.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Quote created and sent to user successfully!')
            return redirect('admin_view_request', request_id=request_id)
        else:
            messages.error(request, f'Form errors: {form.errors}')
    else:
        cr = custom_request
        duration = cr.get_duration_days() or 7
        mid_budget = round((cr.budget_min + cr.budget_max) / 2, 2)
        total = round(mid_budget * cr.num_travelers, 2)

        # Build smart pre-fills from the request
        guide_line = 'Professional licensed guide\n' if cr.guide_required else ''
        accommodation_line = f'Accommodation: {cr.accommodation_preference}\n' if cr.accommodation_preference else 'Tea house / lodge accommodation\n'

        initial_data = {
            'package_title': f'{cr.destination} {cr.get_activity_type_display()} Package — {cr.num_travelers} Pax',
            'description': (
                f'Custom {cr.get_activity_type_display().lower()} package to {cr.destination}, Nepal.\n'
                f'Dates: {cr.preferred_start_date} to {cr.preferred_end_date} ({duration} days)\n'
                f'Group size: {cr.num_travelers} traveler(s)\n'
                + (f'Special requirements: {cr.special_requirements}\n' if cr.special_requirements else '')
            ),
            'itinerary': '\n'.join([f'Day {i+1}: ' for i in range(min(duration, 10))]),
            'inclusions': (
                f'All ground transportation\n'
                f'{guide_line}'
                f'{accommodation_line}'
                f'All meals (breakfast, lunch, dinner)\n'
                f'All necessary permits and entry fees\n'
                f'First aid kit'
            ),
            'exclusions': (
                'International airfare\n'
                'Travel insurance\n'
                'Personal expenses\n'
                'Tips and gratuities'
            ),
            'price_per_person': mid_budget,
            'total_price': total,
            'validity_days': max(7, (cr.preferred_start_date - timezone.now().date()).days - 7),
            'terms_and_conditions': (
                'Full payment required before trip commencement.\n'
                'Cancellation policy applies as per TrekNepal terms.\n'
                'Itinerary subject to change due to weather or unforeseen circumstances.'
            ),
        }
        form = RequestQuoteForm(initial=initial_data)
    
    context = {
        'form': form,
        'custom_request': custom_request,
    }
    return render(request, 'custom_requests/admin_create_quote.html', context)
