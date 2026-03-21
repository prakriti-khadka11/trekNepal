from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum
import json
import requests
from django.conf import settings

from .models import (
    TravelPackage, Destination, Booking, Trekking, PeakClimbing,
    TravelExpense, TravelBudget, TravelWishlist, Guide
)


def get_db_context(user):
    """Fetch relevant data from the database to give Gemini context about the system."""
    context = {}

    # --- Packages ---
    packages = TravelPackage.objects.select_related('destination').all()[:20]
    context['packages'] = [
        {
            'title': p.title,
            'destination': p.destination.name,
            'price_npr': float(p.price),
            'duration_days': p.duration,
            'available_seats': p.available_seats,
            'description': p.short_description or ''
        }
        for p in packages
    ]

    # --- Trekking routes ---
    treks = Trekking.objects.filter(is_active=True)[:10]
    context['trekking_routes'] = [
        {
            'title': t.title,
            'country': t.country,
            'duration': t.duration,
            'difficulty': t.difficulty,
            'max_altitude': t.max_altitude or 'N/A',
            'price_npr': float(t.price)
        }
        for t in treks
    ]

    # --- Peak climbing ---
    peaks = PeakClimbing.objects.filter(is_active=True)[:10]
    context['peak_climbing'] = [
        {
            'title': p.title,
            'height': p.height,
            'duration': p.duration,
            'difficulty': p.difficulty,
            'price_npr': float(p.price)
        }
        for p in peaks
    ]

    # --- Destinations ---
    destinations = Destination.objects.all()[:10]
    context['destinations'] = [
        {'name': d.name, 'location': d.location}
        for d in destinations
    ]

    # --- User's bookings ---
    bookings = Booking.objects.filter(user=user).select_related('travel_package').order_by('-booking_date')[:10]
    context['my_bookings'] = [
        {
            'package': b.travel_package.title if b.travel_package else 'N/A',
            'travel_date': str(b.travel_date),
            'people': b.num_people,
            'total_price_npr': float(b.total_price),
            'status': b.status
        }
        for b in bookings
    ]

    # --- User's expenses ---
    expenses = TravelExpense.objects.filter(user=user).order_by('-date')[:10]
    total_spent = TravelExpense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    context['my_expenses'] = {
        'total_spent_npr': float(total_spent),
        'recent': [
            {'title': e.title, 'amount': float(e.amount), 'date': str(e.date)}
            for e in expenses
        ]
    }

    # --- User's budgets ---
    budgets = TravelBudget.objects.filter(user=user, is_active=True)[:5]
    context['my_budgets'] = [
        {
            'title': b.title,
            'destination': b.destination,
            'total_budget_npr': float(b.total_budget),
            'remaining_npr': float(b.remaining_budget())
        }
        for b in budgets
    ]

    # --- User's wishlist ---
    wishlist = TravelWishlist.objects.filter(user=user)[:5]
    context['my_wishlist'] = [
        {'destination': w.destination, 'country': w.country, 'priority': w.priority}
        for w in wishlist
    ]

    # --- Guides ---
    guides = Guide.objects.filter(verified=True)[:5]
    context['verified_guides'] = [
        {
            'name': g.user.get_full_name() or g.user.username,
            'experience_years': g.experience_years,
            'languages': g.languages
        }
        for g in guides
    ]

    return context


def ask_gemini(user_message, db_context, username):
    """Send user message + database context to Gemini and return the response."""
    api_key = settings.GEMINI_API_KEY

    system_prompt = f"""You are a helpful AI travel assistant for TrekNepal, a Nepal travel booking website.
You have access to the following real data from the TrekNepal database. Use it to answer the user's questions accurately.

USER: {username}

DATABASE CONTEXT:
{json.dumps(db_context, indent=2)}

INSTRUCTIONS:
- Answer based on the real data above. If the user asks about packages, bookings, expenses, etc., use the actual data.
- Be friendly, concise, and helpful.
- If the user asks about their bookings/expenses/wishlist, refer to the my_bookings, my_expenses, my_wishlist sections.
- If the user asks about available packages or treks, refer to packages and trekking_routes.
- Format responses clearly. Use bullet points where helpful.
- If you don't have enough data to answer, say so honestly.
- Keep responses under 300 words unless the user asks for detailed information.
- Do not make up prices, dates, or package names that are not in the data.
"""

    payload = {
        "contents": [{"parts": [{"text": system_prompt + "\n\nUser question: " + user_message}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
    }

    # Try models in order until one works
    models = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash"]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 429:
                continue  # try next model
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            continue

    return "I'm currently busy. Please wait a moment and try again."


@login_required
def chatbot_interface(request):
    """Render chatbot interface"""
    return render(request, 'chatbot/interface.html')


@csrf_exempt
@login_required
def chatbot_message(request):
    """Handle chatbot messages via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'success': False, 'error': 'Message cannot be empty'})

            # Get real database context
            db_context = get_db_context(request.user)

            # Ask Gemini with the context
            ai_response = ask_gemini(user_message, db_context, request.user.username)

            return JsonResponse({
                'success': True,
                'response': ai_response,
                'timestamp': timezone.now().isoformat()
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})
