from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    TravelExpense, ExpenseCategory, TravelBudget, 
    TravelWishlist, TravelDocument, UserPreference,
    Booking, TravelPackage  # Import existing booking models
)
from django.contrib.auth.models import User
import json

@login_required
def personal_dashboard(request):
    """Personal dashboard with overview of all features and booking integration"""
    user_expenses = TravelExpense.objects.filter(user=request.user)
    user_budgets = TravelBudget.objects.filter(user=request.user)
    user_wishlist = TravelWishlist.objects.filter(user=request.user)
    user_documents = TravelDocument.objects.filter(user=request.user)
    
    # Get user's actual bookings
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    recent_bookings = user_bookings[:3]
    
    # Calculate total booking costs
    total_booking_cost = user_bookings.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Get recent expenses
    recent_expenses = user_expenses.order_by('-date')[:5]
    
    # Budget alerts
    budget_alerts = []
    active_budgets = user_budgets.filter(is_active=True)
    
    for budget in active_budgets:
        percentage = budget.budget_percentage()
        if percentage > 90:
            budget_alerts.append({
                'type': 'danger',
                'message': f'Budget "{budget.title}" is {percentage:.1f}% spent! You\'re over budget.',
                'budget': budget
            })
        elif percentage > 75:
            budget_alerts.append({
                'type': 'warning', 
                'message': f'Budget "{budget.title}" is {percentage:.1f}% spent. Consider reducing expenses.',
                'budget': budget
            })
    
    # Document expiry alerts
    document_alerts = []
    expiring_docs = [doc for doc in user_documents if doc.is_expiring_soon()]
    if expiring_docs:
        document_alerts.append({
            'type': 'warning',
            'message': f'{len(expiring_docs)} document(s) expiring within 30 days. Please renew them.',
            'count': len(expiring_docs)
        })
    
    context = {
        'total_expenses': user_expenses.count(),
        'active_budgets': active_budgets.count(),
        'wishlist_count': user_wishlist.count(),
        'documents_count': user_documents.count(),
        'recent_expenses': recent_expenses,
        'recent_bookings': recent_bookings,
        'total_booking_cost': total_booking_cost,
        'budget_alerts': budget_alerts,
        'document_alerts': document_alerts,
        'total_bookings': user_bookings.count(),
    }
    
    return render(request, 'personal/dashboard.html', context)

@login_required
def expense_tracker(request):
    """Enhanced expense tracker with booking integration and professional features"""
    # Store referrer for back navigation
    referrer = request.META.get('HTTP_REFERER', '')
    # Only store if it's a different page (not expense tracker itself)
    if referrer and 'expenses' not in referrer:
        request.session['expense_tracker_back'] = referrer

    back_url = request.session.get('expense_tracker_back', '')
    # Auto-create expenses from bookings (without changing booking logic)
    sync_booking_expenses(request.user)
    
    user_expenses = TravelExpense.objects.filter(user=request.user)
    categories = ExpenseCategory.objects.all()
    
    # Apply filters
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'bookings':
        filtered_expenses = user_expenses.filter(is_booking_expense=True)
    elif filter_type == 'manual':
        filtered_expenses = user_expenses.filter(is_booking_expense=False)
    elif filter_type == 'this-month':
        current_month = timezone.now().month
        current_year = timezone.now().year
        filtered_expenses = user_expenses.filter(
            date__month=current_month,
            date__year=current_year
        )
    else:
        filtered_expenses = user_expenses
    
    # Order by date (most recent first)
    filtered_expenses = filtered_expenses.order_by('-date', '-created_at')[:20]
    
    # Get current month expenses
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_expenses = user_expenses.filter(
        date__month=current_month,
        date__year=current_year
    )
    
    # Calculate enhanced statistics
    total_spent = user_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_total = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    booking_expenses_count = user_expenses.filter(is_booking_expense=True).count()
    avg_expense = total_spent / user_expenses.count() if user_expenses.count() > 0 else 0
    
    # Category-wise expenses for chart
    category_data = []
    for category in categories:
        category_total = user_expenses.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        if category_total > 0:
            category_data.append({
                'name': category.name,
                'amount': float(category_total),
                'color': category.color
            })
    
    # Monthly trend data (last 6 months)
    monthly_trend = []
    for i in range(6):
        month_date = timezone.now() - timedelta(days=30*i)
        month_expenses = user_expenses.filter(
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_trend.append({
            'month': month_date.strftime('%b %Y'),
            'amount': float(month_expenses)
        })
    monthly_trend.reverse()
    
    context = {
        'total_spent': total_spent,
        'monthly_total': monthly_total,
        'categories': categories,
        'category_data': json.dumps(category_data),
        'monthly_trend': json.dumps(monthly_trend),
        'filtered_expenses': filtered_expenses,
        'expense_count': user_expenses.count(),
        'booking_expenses_count': booking_expenses_count,
        'avg_expense': avg_expense,
        'current_filter': filter_type,
        'paid_bookings': Booking.objects.filter(user=request.user, status='PAID').select_related('travel_package__destination', 'trekking').order_by('travel_date'),
        'back_url': back_url,
    }
    
    return render(request, 'personal/expense_tracker.html', context)

def sync_booking_expenses(user):
    """Automatically create expense entries for user's bookings"""
    from .models import Booking
    
    # Get all paid bookings that don't have corresponding expenses
    bookings = Booking.objects.filter(
        user=user, 
        status='PAID'
    ).exclude(
        id__in=TravelExpense.objects.filter(
            user=user, 
            is_booking_expense=True
        ).values_list('booking_id', flat=True)
    )
    
    # Get or create "Travel Package" category for bookings
    booking_category, created = ExpenseCategory.objects.get_or_create(
        name='Travel Package',
        defaults={
            'icon': 'fas fa-suitcase-rolling',
            'color': '#17a2b8'
        }
    )
    
    # Create expense entries for bookings
    for booking in bookings:
        TravelExpense.objects.create(
            user=user,
            category=booking_category,
            title=f"Booking: {booking.travel_package.title if booking.travel_package else 'Travel Package'}",
            amount=booking.total_price,
            currency='NPR',  # Assuming NPR for bookings
            date=booking.travel_date,
            location=booking.travel_package.destination.name if booking.travel_package else '',
            notes=f"Automatically created from booking #{booking.id}. {booking.num_people} people.",
            is_booking_expense=True,
            booking_id=booking.id
        )

@login_required
def add_expense(request):
    """Add new travel expense"""
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            category = get_object_or_404(ExpenseCategory, id=category_id)
            booking_id = request.POST.get('booking_id') or None

            expense = TravelExpense.objects.create(
                user=request.user,
                category=category,
                title=request.POST.get('title'),
                amount=request.POST.get('amount'),
                currency=request.POST.get('currency', 'NPR'),
                date=request.POST.get('date'),
                location=request.POST.get('location', ''),
                notes=request.POST.get('notes', ''),
                booking_id=int(booking_id) if booking_id else None,
                is_booking_expense=False,
            )

            if request.FILES.get('receipt_image'):
                expense.receipt_image = request.FILES['receipt_image']
                expense.save()

            messages.success(request, 'Expense added successfully!')
            # Redirect back to budget page if came from there
            if booking_id:
                return redirect('travel_budget')
            return redirect('expense_tracker')

        except Exception as e:
            messages.error(request, f'Error adding expense: {str(e)}')

    categories = ExpenseCategory.objects.all()
    return render(request, 'personal/add_expense.html', {'categories': categories})

@login_required
def travel_budget(request):
    """Travel budget — upcoming bookings only, booking price auto-counted."""
    from datetime import date

    today = date.today()

    # Only UPCOMING paid bookings — deduplicate by destination (keep soonest)
    all_upcoming = Booking.objects.filter(
        user=request.user,
        status='PAID',
        travel_date__gte=today,
    ).select_related('travel_package', 'travel_package__destination', 'trekking').order_by('travel_date')

    # Deduplicate: one card per unique destination
    seen_dests = {}
    for b in all_upcoming:
        dest = (
            b.travel_package.destination.name if b.travel_package
            else b.trekking.title if b.trekking
            else f'Booking #{b.id}'
        )
        if dest not in seen_dests:
            seen_dests[dest] = b
    upcoming_bookings = list(seen_dests.values())

    # For each upcoming booking, find or build budget data
    booking_budgets = []
    for b in upcoming_bookings:
        dest = (
            b.travel_package.destination.name if b.travel_package
            else b.trekking.title if b.trekking
            else ''
        )
        pkg_title = (
            b.travel_package.title if b.travel_package
            else b.trekking.title if b.trekking
            else f'Booking #{b.id}'
        )
        # Find budget — exact destination match + travel date within range
        budget = TravelBudget.objects.filter(
            user=request.user,
            destination__iexact=dest,
            start_date__lte=b.travel_date,
            end_date__gte=b.travel_date,
        ).order_by('-created_at').first()

        # Expenses for this destination in the travel date range
        if budget:
            manual_expenses = TravelExpense.objects.filter(
                user=request.user,
                is_booking_expense=False,
            ).filter(
                # Match by booking_id OR by location containing destination
                Q(booking_id=b.id) |
                Q(location__icontains=dest, date__range=[budget.start_date, budget.end_date])
            ).distinct()
            manual_spent = manual_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            total_spent = float(b.total_price) + float(manual_spent)
            remaining = float(budget.total_budget) - total_spent
            pct = (total_spent / float(budget.total_budget) * 100) if budget.total_budget > 0 else 0
        else:
            manual_expenses = []
            manual_spent = 0
            total_spent = float(b.total_price)
            remaining = 0
            pct = 0

        booking_budgets.append({
            'booking': b,
            'dest': dest,
            'pkg_title': pkg_title,
            'budget': budget,
            'booking_cost': float(b.total_price),
            'manual_spent': float(manual_spent),
            'total_spent': total_spent,
            'remaining': remaining,
            'pct': round(pct, 1),
            'alert_50': budget and pct >= 50 and pct < 75,
            'alert_75': budget and pct >= 75 and pct < 100,
            'alert_over': budget and pct >= 100,
            'manual_expenses': manual_expenses if budget else [],
        })

    context = {
        'booking_budgets': booking_budgets,
        'categories': ExpenseCategory.objects.all(),
    }
    return render(request, 'personal/travel_budget.html', context)

@login_required
def update_budget(request, budget_id):
    """Update total budget amount."""
    if request.method == 'POST':
        budget = get_object_or_404(TravelBudget, id=budget_id, user=request.user)
        try:
            budget.total_budget = request.POST.get('total_budget')
            budget.save()
            messages.success(request, 'Budget updated.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('travel_budget')


@login_required
def add_budget(request):
    """Add new travel budget — linked to a booking."""
    if request.method == 'POST':
        try:
            booking_id = request.POST.get('booking_id')
            booking = None
            dest = request.POST.get('destination', '')
            start = request.POST.get('start_date')
            end = request.POST.get('end_date')

            if booking_id:
                booking = Booking.objects.filter(id=booking_id, user=request.user).first()
                if booking:
                    dest = (
                        booking.travel_package.destination.name if booking.travel_package
                        else booking.trekking.title if booking.trekking
                        else dest
                    )
                    start = str(booking.travel_date)
                    from datetime import timedelta, date
                    import re
                    dur_str = (booking.travel_package.duration if booking.travel_package
                               else booking.trekking.duration if booking.trekking else '7')
                    dur_match = re.search(r'(\d+)', str(dur_str))
                    dur = int(dur_match.group(1)) if dur_match else 7
                    end = str(booking.travel_date + timedelta(days=dur))

            TravelBudget.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                total_budget=request.POST.get('total_budget'),
                currency='NPR',
                start_date=start,
                end_date=end,
                destination=dest,
            )
            messages.success(request, 'Budget created successfully!')
            return redirect('travel_budget')
        except Exception as e:
            messages.error(request, f'Error creating budget: {str(e)}')

    return redirect('travel_budget')

@login_required
def travel_wishlist(request):
    """Travel wishlist management"""
    wishlist_items = TravelWishlist.objects.filter(user=request.user).order_by('-priority', 'target_date')
    completed_items = wishlist_items.filter(is_completed=True)
    pending_items = wishlist_items.filter(is_completed=False)
    
    context = {
        'wishlist_items': wishlist_items,
        'completed_items': completed_items,
        'pending_items': pending_items,
        'total_items': wishlist_items.count(),
        'completed_count': completed_items.count()
    }
    
    return render(request, 'personal/travel_wishlist.html', context)

@login_required
def add_wishlist_item(request):
    """Add item to travel wishlist"""
    if request.method == 'POST':
        try:
            TravelWishlist.objects.create(
                user=request.user,
                destination=request.POST.get('destination'),
                country=request.POST.get('country'),
                estimated_cost=request.POST.get('estimated_cost') or None,
                currency=request.POST.get('currency', 'NPR'),
                priority=request.POST.get('priority', 'medium'),
                target_date=request.POST.get('target_date') or None,
                notes=request.POST.get('notes', '')
            )
            messages.success(request, 'Destination added to wishlist!')
            return redirect('travel_wishlist')
        except Exception as e:
            messages.error(request, f'Error adding to wishlist: {str(e)}')
    
    return render(request, 'personal/add_wishlist.html')

@login_required
def travel_documents(request):
    """Travel documents management"""
    documents = TravelDocument.objects.filter(user=request.user).order_by('expiry_date')
    expiring_soon = [doc for doc in documents if doc.is_expiring_soon()]
    
    context = {
        'documents': documents,
        'expiring_soon': expiring_soon,
        'total_documents': documents.count(),
        'expiring_count': len(expiring_soon)
    }
    
    return render(request, 'personal/travel_documents.html', context)

@login_required
def add_document(request):
    """Add new travel document"""
    if request.method == 'POST':
        try:
            document = TravelDocument.objects.create(
                user=request.user,
                document_type=request.POST.get('document_type'),
                title=request.POST.get('title'),
                document_number=request.POST.get('document_number', ''),
                issue_date=request.POST.get('issue_date') or None,
                expiry_date=request.POST.get('expiry_date') or None,
                issuing_authority=request.POST.get('issuing_authority', ''),
                notes=request.POST.get('notes', '')
            )
            
            if request.FILES.get('document_file'):
                document.document_file = request.FILES['document_file']
                document.save()
            
            messages.success(request, 'Document added successfully!')
            return redirect('travel_documents')
        except Exception as e:
            messages.error(request, f'Error adding document: {str(e)}')
    
    return render(request, 'personal/add_document.html')

@login_required
def user_preferences(request):
    """User preferences management"""
    try:
        preferences = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        preferences = UserPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
        try:
            preferences.preferred_currency = request.POST.get('preferred_currency', 'NPR')
            preferences.budget_alerts = request.POST.get('budget_alerts') == 'on'
            preferences.document_expiry_alerts = request.POST.get('document_expiry_alerts') == 'on'
            preferences.emergency_contact_name = request.POST.get('emergency_contact_name', '')
            preferences.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
            preferences.emergency_contact_email = request.POST.get('emergency_contact_email', '')
            preferences.travel_style = request.POST.get('travel_style', 'comfort')
            preferences.save()
            
            messages.success(request, 'Preferences updated successfully!')
            return redirect('user_preferences')
        except Exception as e:
            messages.error(request, f'Error updating preferences: {str(e)}')
    
    context = {
        'preferences': preferences
    }
    
    return render(request, 'personal/user_preferences.html', context)

@login_required
def expense_analytics_api(request):
    """API endpoint for expense analytics data"""
    user_expenses = TravelExpense.objects.filter(user=request.user)
    
    # Get date range from request
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    filtered_expenses = user_expenses.filter(date__gte=start_date)
    
    # Daily expenses for chart
    daily_data = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_expenses = filtered_expenses.filter(date=day.date()).aggregate(Sum('amount'))['amount__sum'] or 0
        daily_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'amount': float(day_expenses)
        })
    
    return JsonResponse({
        'daily_data': daily_data,
        'total_amount': float(filtered_expenses.aggregate(Sum('amount'))['amount__sum'] or 0),
        'expense_count': filtered_expenses.count()
    })

@login_required
def toggle_wishlist_status(request, item_id):
    """Toggle wishlist item completion status"""
    if request.method == 'POST':
        try:
            item = get_object_or_404(TravelWishlist, id=item_id, user=request.user)
            item.is_completed = not item.is_completed
            if item.is_completed:
                item.completed_date = timezone.now().date()
            else:
                item.completed_date = None
            item.save()
            
            return JsonResponse({
                'success': True,
                'is_completed': item.is_completed,
                'message': 'Wishlist item updated successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def export_expenses(request):
    """Export user expenses to CSV"""
    import csv
    from django.http import HttpResponse
    
    # Get user's expenses
    expenses = TravelExpense.objects.filter(user=request.user).order_by('-date')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="expenses_{request.user.username}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Date', 'Title', 'Category', 'Amount', 'Currency', 
        'Location', 'Notes', 'Type', 'Created At'
    ])
    
    # Write expense data
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.title,
            expense.category.name,
            str(expense.amount),
            expense.currency,
            expense.location or '',
            expense.notes or '',
            'Booking' if expense.is_booking_expense else 'Manual',
            expense.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response