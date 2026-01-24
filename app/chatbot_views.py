from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
import json
import re
from datetime import datetime, timedelta

from .models import (
    TravelPackage, Destination, Country, Booking, Review, Trekking, PeakClimbing,
    TravelExpense, ExpenseCategory, TravelBudget, TravelWishlist, TravelDocument,
    AltitudeProfile, AcclimatizationPlan, SymptomLog, EmergencyProtocol
)
from emergency.models import EmergencyAlert
from emergency.data import districts

class TrekNepalAI:
    """
    Advanced AI Assistant for TrekNepal - Provides intelligent, context-aware responses
    by analyzing user data, travel patterns, and providing personalized recommendations.
    """
    def __init__(self, user):
        self.user = user
        self._build_user_profile()
        
    def _build_user_profile(self):
        """Build comprehensive user profile for personalized responses"""
        try:
            self.user_profile = {
                'bookings': Booking.objects.filter(user=self.user),
                'expenses': TravelExpense.objects.filter(user=self.user),
                'budgets': TravelBudget.objects.filter(user=self.user),
                'wishlist': TravelWishlist.objects.filter(user=self.user),
                'documents': TravelDocument.objects.filter(user=self.user),
                'total_spent': TravelExpense.objects.filter(user=self.user).aggregate(Sum('amount'))['amount__sum'] or 0,
                'booking_count': Booking.objects.filter(user=self.user).count(),
                'travel_experience': 'experienced' if Booking.objects.filter(user=self.user).count() > 3 else 'beginner'
            }
            
            # Add altitude profile if exists
            try:
                self.user_profile['altitude_profile'] = AltitudeProfile.objects.get(user=self.user)
                self.user_profile['altitude_logs'] = SymptomLog.objects.filter(user=self.user).order_by('-date')[:5]
            except AltitudeProfile.DoesNotExist:
                self.user_profile['altitude_profile'] = None
                self.user_profile['altitude_logs'] = []
                
        except Exception as e:
            # Fallback profile if there are any database issues
            self.user_profile = {
                'bookings': Booking.objects.none(),
                'expenses': TravelExpense.objects.none(),
                'budgets': TravelBudget.objects.none(),
                'wishlist': TravelWishlist.objects.none(),
                'documents': TravelDocument.objects.none(),
                'total_spent': 0,
                'booking_count': 0,
                'travel_experience': 'beginner',
                'altitude_profile': None,
                'altitude_logs': []
            }
        
    def process_query(self, query):
        """Advanced query processing with AI-like intelligence"""
        try:
            query_lower = query.lower()
            
            # Intelligent greeting with user analysis
            if any(word in query_lower for word in ['hello', 'hi', 'hey', 'namaste', 'start']):
                return self._generate_intelligent_greeting()
            
            # Advanced booking analytics
            if any(word in query_lower for word in ['booking', 'trip', 'travel', 'reservation']):
                return self._analyze_bookings(query_lower)
            
            # Package information and search
            if any(word in query_lower for word in ['package', 'packages', 'tour', 'trek', 'climbing', 'available', 'search']):
                return self._package_intelligence(query_lower)
            
            # Financial intelligence and insights
            if any(word in query_lower for word in ['expense', 'cost', 'budget', 'money', 'financial', 'spending']):
                return self._financial_analysis(query_lower)
            
            # Destination intelligence and recommendations
            if any(word in query_lower for word in ['destination', 'place', 'where', 'location']):
                return self._destination_intelligence(query_lower)
            
            # Health and altitude intelligence
            if any(word in query_lower for word in ['altitude', 'health', 'symptom', 'sick', 'oxygen', 'medical']):
                return self._health_intelligence(query_lower)
            
            # Emergency and safety intelligence
            if any(word in query_lower for word in ['emergency', 'help', 'rescue', 'hospital', 'safety', 'danger']):
                return self._safety_intelligence(query_lower)
            
            # Travel planning intelligence
            if any(word in query_lower for word in ['plan', 'prepare', 'advice', 'tip', 'guide']):
                return self._travel_planning_intelligence()
            
            # Weather and conditions
            if any(word in query_lower for word in ['weather', 'climate', 'season', 'temperature']):
                return self._weather_intelligence()
            
            # Advanced analytics and insights
            if any(word in query_lower for word in ['analyze', 'insight', 'report', 'summary', 'overview']):
                return self._generate_travel_insights()
            
            return self._intelligent_fallback(query)
            
        except Exception as e:
            return f"🤖 **AI System Notice:**\n\nI encountered an issue while processing your request. Let me help you with some basic information instead.\n\n**I can assist you with:**\n• Your bookings and travel history\n• Expense tracking and budgets\n• Destination recommendations\n• Altitude safety guidance\n• Emergency information\n\nPlease try asking a specific question like 'show my bookings' or 'recommend destinations'."
    
    def _generate_intelligent_greeting(self):
        """Generate personalized, intelligent greeting based on user data"""
        try:
            name = self.user.first_name or self.user.username
            
            greeting = f"🙏 **Namaste {name}!** Welcome to your AI Travel Assistant.\n\n"
            
            # Intelligent user analysis
            if self.user_profile['booking_count'] == 0:
                greeting += "🌟 **New Explorer Detected!** I'm excited to help you plan your first Nepal adventure.\n\n"
                greeting += "**I can assist you with:**\n"
                greeting += "• 🏔️ **Destination Recommendations** - Find perfect treks based on your preferences\n"
                greeting += "• 💰 **Budget Planning** - Calculate costs and create travel budgets\n"
                greeting += "• 🏥 **Safety Guidance** - Altitude sickness prevention and emergency protocols\n"
                greeting += "• 📋 **Trip Planning** - Complete travel preparation assistance\n\n"
            elif self.user_profile['travel_experience'] == 'experienced':
                greeting += f"🎖️ **Experienced Traveler Recognized!** With {self.user_profile['booking_count']} trips completed, you're a true Nepal explorer.\n\n"
            else:
                greeting += f"🚀 **Adventure Continues!** You've completed {self.user_profile['booking_count']} trips. Ready for your next challenge?\n\n"
            
            # Add personalized insights
            if self.user_profile['total_spent'] > 0:
                greeting += f"💡 **Quick Insight:** You've invested NPR {self.user_profile['total_spent']:,.0f} in Nepal adventures.\n"
            
            if self.user_profile['altitude_profile']:
                risk_level = self.user_profile['altitude_profile'].get_risk_level()
                greeting += f"🏔️ **Altitude Profile:** {risk_level.title()} risk level detected.\n"
            
            greeting += "\n**What would you like to explore today?**"
            return greeting
            
        except Exception as e:
            return f"🙏 **Namaste {self.user.first_name or self.user.username}!** Welcome to your AI Travel Assistant.\n\nI'm here to help you with your Nepal travel experience. Ask me about bookings, expenses, destinations, or safety information!"
    
    def _analyze_bookings(self, query):
        """Advanced booking analysis with AI insights"""
        try:
            bookings = self.user_profile['bookings'].order_by('-booking_date')
            
            if bookings.exists():
                response = f"📋 **Complete Booking Portfolio:**\n\n"
                
                paid_bookings = bookings.filter(status='PAID')
                pending_bookings = bookings.filter(status='PENDING')
                
                response += f"✅ **Confirmed Trips:** {paid_bookings.count()}\n"
                response += f"⏳ **Pending Confirmations:** {pending_bookings.count()}\n"
                response += f"💰 **Total Investment:** NPR {self.user_profile['total_spent']:,.0f}\n\n"
                
                # Show recent bookings
                response += "🏔️ **Recent Bookings:**\n"
                for booking in bookings[:3]:
                    status_emoji = "✅" if booking.status == "PAID" else "⏳" if booking.status == "PENDING" else "❌"
                    response += f"{status_emoji} **{booking.travel_package.title if booking.travel_package else 'Travel Package'}**\n"
                    response += f"   📅 Date: {booking.travel_date}\n"
                    response += f"   👥 People: {booking.num_people}\n"
                    response += f"   💰 Cost: NPR {booking.total_price:,.0f}\n\n"
                
                return response
            else:
                return self._suggest_new_bookings()
                
        except Exception as e:
            return "📋 **Booking Information:**\n\nI can help you with your travel bookings! Ask me about:\n• Your upcoming trips\n• Booking history\n• New destination recommendations\n• Travel planning assistance"
    
    def _suggest_new_bookings(self):
        """AI-powered booking suggestions"""
        try:
            # Get popular packages
            popular_packages = TravelPackage.objects.all()[:5]
            
            response = "🌟 **AI-Powered Adventure Recommendations:**\n\n"
            response += "Based on current trends and traveler preferences, here are perfect matches for you:\n\n"
            
            for i, package in enumerate(popular_packages, 1):
                difficulty = "Beginner-Friendly" if package.duration <= 7 else "Intermediate" if package.duration <= 14 else "Advanced"
                
                response += f"**{i}. {package.title}** 🏔️\n"
                response += f"   📍 Location: {package.destination.name}\n"
                response += f"   ⏱️ Duration: {package.duration} days\n"
                response += f"   📊 Difficulty: {difficulty}\n"
                response += f"   💰 Investment: NPR {package.price:,.0f}\n"
                response += f"   🪑 Availability: {package.available_seats} seats\n\n"
            
            response += "💡 **AI Recommendation:** Start with shorter treks if you're new to high-altitude adventures!"
            return response
            
        except Exception as e:
            return "🌟 **Adventure Recommendations:**\n\nI'd love to help you find the perfect Nepal adventure! Visit our packages page to explore:\n• Trekking adventures\n• Cultural tours\n• Peak climbing expeditions\n• Wildlife safaris\n\nAsk me about specific destinations for personalized recommendations!"
    
    def _financial_analysis(self, query):
        """Advanced financial analysis and insights"""
        try:
            expenses = self.user_profile['expenses']
            total_spent = self.user_profile['total_spent']
            
            if expenses.exists():
                response = "💰 **Financial Intelligence Report:**\n\n"
                response += f"• Total Expenses: NPR {total_spent:,.0f}\n"
                response += f"• Total Entries: {expenses.count()}\n\n"
                
                # Recent expenses
                recent_expenses = expenses.order_by('-date')[:5]
                response += "💳 **Recent Activity:**\n"
                for expense in recent_expenses:
                    response += f"• {expense.title}: NPR {expense.amount:,.0f}\n"
                
                return response
            else:
                return "💡 **Start Your Financial Journey!**\n\nTrack your travel expenses to get detailed financial insights and AI-powered recommendations!"
                
        except Exception as e:
            return "💰 **Financial Analysis:**\n\nI can help you analyze your travel expenses and create budgets. Visit the Expense Tracker to start logging your spending!"
    
    def _package_intelligence(self, query):
        """Advanced package search and recommendations with detailed information"""
        try:
            response = "🎯 **Package Intelligence System:**\n\n"
            
            # Determine search intent
            if any(word in query for word in ['everest', 'ebc', 'base camp']):
                packages = TravelPackage.objects.filter(title__icontains='everest')
                response += "🏔️ **Everest Base Camp Adventures:**\n\n"
            elif any(word in query for word in ['annapurna', 'abc']):
                packages = TravelPackage.objects.filter(title__icontains='annapurna')
                response += "🌄 **Annapurna Region Packages:**\n\n"
            elif any(word in query for word in ['langtang']):
                packages = TravelPackage.objects.filter(title__icontains='langtang')
                response += "🏞️ **Langtang Valley Packages:**\n\n"
            elif any(word in query for word in ['peak', 'climbing', 'summit']):
                packages = TravelPackage.objects.filter(title__icontains='peak')
                if not packages.exists():
                    # Also check PeakClimbing model
                    peak_climbs = PeakClimbing.objects.filter(is_active=True)[:5]
                    if peak_climbs.exists():
                        response += "⛰️ **Peak Climbing Adventures:**\n\n"
                        for peak in peak_climbs:
                            response += f"**🏔️ {peak.title}**\n"
                            response += f"   📍 Location: {peak.country}\n"
                            response += f"   📏 Height: {peak.height}\n"
                            response += f"   ⏱️ Duration: {peak.duration}\n"
                            response += f"   📊 Difficulty: {peak.difficulty}\n"
                            response += f"   💰 Price: NPR {peak.price:,.0f}\n"
                            response += f"   🔗 Details: /peak-climbing/{peak.slug}/\n\n"
                        return response
                else:
                    response += "⛰️ **Peak Climbing Packages:**\n\n"
            elif any(word in query for word in ['trek', 'trekking', 'hiking']):
                # Check both TravelPackage and Trekking models
                packages = TravelPackage.objects.all()[:8]
                treks = Trekking.objects.filter(is_active=True)[:5]
                
                response += "🥾 **Trekking Adventures:**\n\n"
                
                # Show dedicated trekking packages first
                if treks.exists():
                    response += "**🏔️ Specialized Trekking Routes:**\n"
                    for trek in treks:
                        response += f"• **{trek.title}** - {trek.duration}\n"
                        response += f"  📍 {trek.country} | 🏔️ Max Alt: {trek.max_altitude or 'N/A'}\n"
                        response += f"  📊 {trek.difficulty} | 💰 NPR {trek.price:,.0f}\n"
                        response += f"  🔗 /trekking/{trek.slug}/\n\n"
                
                response += "**🎒 Travel Packages with Trekking:**\n"
            elif any(word in query for word in ['budget', 'cheap', 'affordable', 'low cost']):
                packages = TravelPackage.objects.filter(price__lt=50000).order_by('price')[:6]
                response += "💰 **Budget-Friendly Packages:**\n\n"
            elif any(word in query for word in ['luxury', 'premium', 'expensive', 'high end']):
                packages = TravelPackage.objects.filter(price__gt=100000).order_by('-price')[:6]
                response += "✨ **Premium Luxury Packages:**\n\n"
            elif any(word in query for word in ['short', 'quick', 'weekend']):
                packages = TravelPackage.objects.filter(duration__lte=5).order_by('duration')[:6]
                response += "⚡ **Short Duration Packages:**\n\n"
            elif any(word in query for word in ['long', 'extended', 'adventure']):
                packages = TravelPackage.objects.filter(duration__gte=14).order_by('-duration')[:6]
                response += "🗓️ **Extended Adventure Packages:**\n\n"
            else:
                # General package search
                packages = TravelPackage.objects.all().order_by('-id')[:8]
                response += "🌟 **Available Travel Packages:**\n\n"
            
            # Display package information
            if packages.exists():
                for i, package in enumerate(packages, 1):
                    # Determine package category
                    category = "🎒 General"
                    if 'everest' in package.title.lower():
                        category = "🏔️ Everest"
                    elif 'annapurna' in package.title.lower():
                        category = "🌄 Annapurna"
                    elif 'langtang' in package.title.lower():
                        category = "🏞️ Langtang"
                    elif any(word in package.title.lower() for word in ['peak', 'climb', 'summit']):
                        category = "⛰️ Peak Climbing"
                    elif any(word in package.title.lower() for word in ['trek', 'hiking']):
                        category = "🥾 Trekking"
                    elif any(word in package.title.lower() for word in ['tour', 'cultural', 'heritage']):
                        category = "🏛️ Cultural Tour"
                    
                    # Difficulty assessment
                    difficulty = "Moderate"
                    if package.duration <= 5:
                        difficulty = "Easy"
                    elif package.duration <= 10:
                        difficulty = "Moderate"
                    elif package.duration <= 15:
                        difficulty = "Challenging"
                    else:
                        difficulty = "Expert"
                    
                    # Availability status
                    availability = "✅ Available" if package.available_seats > 0 else "❌ Fully Booked"
                    if package.available_seats <= 5 and package.available_seats > 0:
                        availability = f"⚠️ Limited ({package.available_seats} seats)"
                    
                    response += f"**{i}. {package.title}** {category}\n"
                    response += f"   📍 **Destination:** {package.destination.name}\n"
                    response += f"   ⏱️ **Duration:** {package.duration} days\n"
                    response += f"   📊 **Difficulty:** {difficulty}\n"
                    response += f"   💰 **Price:** NPR {package.price:,.0f} per person\n"
                    response += f"   🪑 **Availability:** {availability}\n"
                    
                    # Add short description if available
                    if package.short_description:
                        response += f"   📝 **Overview:** {package.short_description[:100]}{'...' if len(package.short_description) > 100 else ''}\n"
                    
                    response += f"   🔗 **Book Now:** /package/{package.id}/\n\n"
                
                # Add personalized recommendations
                response += self._get_package_recommendations()
                
            else:
                response += "❌ **No packages found matching your criteria.**\n\n"
                response += "**Available Categories:**\n"
                response += "• 🏔️ Everest Base Camp Treks\n"
                response += "• 🌄 Annapurna Circuit Adventures\n"
                response += "• 🏞️ Langtang Valley Treks\n"
                response += "• ⛰️ Peak Climbing Expeditions\n"
                response += "• 🏛️ Cultural Heritage Tours\n"
                response += "• 🥾 General Trekking Packages\n\n"
                response += "💡 **Try asking:** 'Show me Everest packages' or 'Budget trekking options'"
            
            return response
            
        except Exception as e:
            return "🎯 **Package Information:**\n\nI can help you find the perfect Nepal adventure! Ask me about:\n• Specific destinations (Everest, Annapurna, Langtang)\n• Package types (trekking, peak climbing, cultural tours)\n• Budget preferences (budget-friendly or luxury)\n• Duration (short trips or extended adventures)\n\nTry: 'Show me Everest Base Camp packages' or 'Budget trekking options'"
    
    def _get_package_recommendations(self):
        """Generate personalized package recommendations based on user profile"""
        try:
            recommendations = "\n💡 **AI Recommendations for You:**\n"
            
            # Based on user experience
            if self.user_profile['travel_experience'] == 'beginner':
                recommendations += "• 🌟 **Beginner-Friendly:** Start with shorter treks (5-7 days)\n"
                recommendations += "• 🏔️ **Altitude Consideration:** Choose packages below 4000m initially\n"
            else:
                recommendations += "• 🎖️ **Experienced Traveler:** Consider challenging high-altitude treks\n"
                recommendations += "• 🏔️ **Next Challenge:** Everest Base Camp or Annapurna Circuit\n"
            
            # Based on budget history
            if self.user_profile['total_spent'] > 0:
                avg_spending = self.user_profile['total_spent'] / max(self.user_profile['booking_count'], 1)
                if avg_spending < 30000:
                    recommendations += "• 💰 **Budget Match:** Focus on packages under NPR 50,000\n"
                elif avg_spending > 80000:
                    recommendations += "• ✨ **Premium Options:** Luxury packages with helicopter transfers\n"
            
            # Based on season
            from datetime import datetime
            current_month = datetime.now().month
            if current_month in [3, 4, 5]:
                recommendations += "• 🌸 **Spring Season:** Perfect time for rhododendron blooms\n"
            elif current_month in [9, 10, 11]:
                recommendations += "• 🍂 **Autumn Season:** Best visibility and stable weather\n"
            elif current_month in [12, 1, 2]:
                recommendations += "• ❄️ **Winter Season:** Lower altitude treks recommended\n"
            else:
                recommendations += "• 🌧️ **Monsoon Season:** Consider rain-shadow areas like Upper Mustang\n"
            
            return recommendations
            
        except Exception as e:
            return "\n💡 **Tip:** Book in advance for better availability and pricing!"
    
    def _destination_intelligence(self, query):
        """AI-powered destination recommendations with detailed information"""
        try:
            response = "🏔️ **Destination Intelligence:**\n\n"
            
            # Specific destination queries
            if any(word in query for word in ['everest', 'ebc', 'base camp']):
                response += "🏔️ **Everest Base Camp Region:**\n"
                response += "• **Altitude:** 5,364m (17,598ft)\n"
                response += "• **Best Season:** March-May, September-November\n"
                response += "• **Duration:** 12-16 days typically\n"
                response += "• **Difficulty:** Challenging\n"
                response += "• **Highlights:** Kala Patthar viewpoint, Sherpa culture, monasteries\n"
                response += "• **Permits Required:** Sagarmatha National Park, TIMS\n\n"
                
            elif any(word in query for word in ['annapurna', 'abc', 'circuit']):
                response += "🌄 **Annapurna Region:**\n"
                response += "• **Annapurna Circuit:** 15-20 days, crosses Thorong La Pass (5,416m)\n"
                response += "• **Annapurna Base Camp:** 7-12 days, reaches 4,130m\n"
                response += "• **Best Season:** March-May, September-November\n"
                response += "• **Highlights:** Diverse landscapes, hot springs, mountain views\n"
                response += "• **Culture:** Gurung and Magar communities\n\n"
                
            elif any(word in query for word in ['langtang']):
                response += "🏞️ **Langtang Valley:**\n"
                response += "• **Altitude:** Up to 4,984m (Tserko Ri)\n"
                response += "• **Duration:** 7-10 days\n"
                response += "• **Difficulty:** Moderate\n"
                response += "• **Highlights:** Tamang culture, cheese factories, mountain views\n"
                response += "• **Best For:** First-time trekkers, cultural experience\n\n"
                
            else:
                # General destination overview
                destinations = Destination.objects.all()[:6]
                response += "🌟 **Popular Nepal Destinations:**\n\n"
                
                for dest in destinations:
                    # Get packages for this destination
                    package_count = TravelPackage.objects.filter(destination=dest).count()
                    
                    response += f"**📍 {dest.name}** - {dest.location}\n"
                    if package_count > 0:
                        response += f"   🎒 {package_count} available packages\n"
                    
                    # Add brief description if available
                    if dest.description:
                        short_desc = dest.description[:120] + "..." if len(dest.description) > 120 else dest.description
                        response += f"   📝 {short_desc}\n"
                    
                    response += f"   🔗 Details: /destination/{dest.id}/\n\n"
            
            # Add seasonal recommendations
            response += self._get_seasonal_recommendations()
            
            return response
            
        except Exception as e:
            return "🏔️ **Destination Recommendations:**\n\nI can help you discover amazing Nepal destinations! Ask me about specific places like 'Everest Base Camp', 'Annapurna Circuit', or 'Langtang Valley'."
    
    def _get_seasonal_recommendations(self):
        """Get season-specific destination recommendations"""
        try:
            from datetime import datetime
            current_month = datetime.now().month
            
            seasonal_info = "\n🗓️ **Seasonal Recommendations:**\n"
            
            if current_month in [3, 4, 5]:  # Spring
                seasonal_info += "🌸 **Spring (Mar-May):** Perfect for all major treks\n"
                seasonal_info += "• Clear mountain views\n"
                seasonal_info += "• Rhododendron blooms\n"
                seasonal_info += "• Moderate temperatures\n"
                
            elif current_month in [6, 7, 8]:  # Monsoon
                seasonal_info += "🌧️ **Monsoon (Jun-Aug):** Limited trekking options\n"
                seasonal_info += "• Upper Mustang (rain-shadow area)\n"
                seasonal_info += "• Dolpo region\n"
                seasonal_info += "• Cultural tours in Kathmandu Valley\n"
                
            elif current_month in [9, 10, 11]:  # Autumn
                seasonal_info += "🍂 **Autumn (Sep-Nov):** Best trekking season\n"
                seasonal_info += "• Crystal clear mountain views\n"
                seasonal_info += "• Stable weather conditions\n"
                seasonal_info += "• Perfect for all altitude levels\n"
                
            else:  # Winter
                seasonal_info += "❄️ **Winter (Dec-Feb):** Lower altitude treks\n"
                seasonal_info += "• Ghorepani Poon Hill\n"
                seasonal_info += "• Langtang Valley (lower sections)\n"
                seasonal_info += "• Cultural tours and wildlife safaris\n"
            
            return seasonal_info
            
        except Exception as e:
            return "\n💡 **Tip:** Check seasonal conditions before booking!"
    
    def _health_intelligence(self, query):
        """Advanced health and altitude intelligence"""
        try:
            altitude_profile = self.user_profile['altitude_profile']
            
            if altitude_profile:
                risk_level = altitude_profile.get_risk_level()
                response = f"🏥 **Health Intelligence:**\n\n"
                response += f"• Risk Level: {risk_level.title()}\n"
                response += f"• Age: {altitude_profile.age} years\n"
                response += f"• Fitness: {altitude_profile.get_fitness_level_display()}\n"
                response += f"• Max Altitude: {altitude_profile.max_altitude_reached}m\n\n"
                response += "Visit Altitude Safety for detailed health monitoring!"
                return response
            else:
                return "🏥 **Health & Safety:**\n\nCreate your altitude profile to get personalized health recommendations and safety guidance for high-altitude adventures!"
                
        except Exception as e:
            return "🏥 **Health & Safety:**\n\nI can help with altitude safety, symptom tracking, and emergency protocols. Visit the Altitude Safety section for comprehensive health monitoring!"
    
    def _safety_intelligence(self, query):
        """Advanced safety and emergency intelligence"""
        try:
            response = "🚨 **Safety Intelligence:**\n\n"
            response += "**Emergency Numbers:**\n"
            response += "• Police: 100\n"
            response += "• Ambulance: 102\n"
            response += "• Tourist Helpline: 1144\n\n"
            response += "Visit Emergency section for detailed protocols and hospital information!"
            return response
            
        except Exception as e:
            return "🚨 **Emergency Information:**\n\nI can provide emergency contacts, hospital locations, and safety protocols. For immediate emergencies, call 100 (Police) or 102 (Ambulance)."
    
    def _travel_planning_intelligence(self):
        """AI-powered travel planning assistance"""
        try:
            response = "🎯 **Travel Planning Intelligence:**\n\n"
            response += "**Essential Preparation:**\n"
            response += "• 🏥 Medical checkup and vaccinations\n"
            response += "• 🥾 Break in trekking boots\n"
            response += "• 💪 Start fitness training\n"
            response += "• 📄 Obtain permits and visas\n"
            response += "• 🏦 Get travel insurance\n\n"
            response += "Ask me about specific aspects of travel planning!"
            return response
            
        except Exception as e:
            return "🎯 **Travel Planning:**\n\nI can help you plan your Nepal adventure! Ask me about packing, preparation, best seasons, or specific destinations."
    
    def _weather_intelligence(self):
        """AI weather and climate intelligence"""
        try:
            response = "🌤️ **Weather Intelligence:**\n\n"
            response += "**Best Seasons:**\n"
            response += "• 🌸 Spring (Mar-May): Clear views, mild weather\n"
            response += "• 🍂 Autumn (Sep-Nov): Stable conditions, best visibility\n"
            response += "• ❄️ Winter (Dec-Feb): Clear skies, cold temperatures\n"
            response += "• 🌧️ Summer (Jun-Aug): Monsoon season\n\n"
            response += "Ask me about weather for specific destinations!"
            return response
            
        except Exception as e:
            return "🌤️ **Weather Information:**\n\nI can provide seasonal weather guidance for Nepal trekking. Generally, Spring (Mar-May) and Autumn (Sep-Nov) are the best seasons for most treks."
    
    def _generate_travel_insights(self):
        """Generate comprehensive AI travel insights"""
        try:
            response = "🧠 **AI Travel Intelligence:**\n\n"
            response += f"**Your Profile:**\n"
            response += f"• Experience: {self.user_profile['travel_experience'].title()}\n"
            response += f"• Total Trips: {self.user_profile['booking_count']}\n"
            response += f"• Investment: NPR {self.user_profile['total_spent']:,.0f}\n\n"
            response += "**Recommendations:**\n"
            response += "• Track expenses for better budgeting\n"
            response += "• Create altitude profile for safety\n"
            response += "• Plan trips during optimal seasons\n"
            return response
            
        except Exception as e:
            return "🧠 **Travel Intelligence:**\n\nI can analyze your travel patterns and provide personalized insights. Ask me about your bookings, expenses, or get destination recommendations!"
    
    def _intelligent_fallback(self, query):
        """Intelligent fallback with query understanding"""
        try:
            response = "🤔 **AI Analysis:**\n\n"
            response += f"I analyzed your query but need more specific information.\n\n"
            response += "**Try asking:**\n"
            response += "• 'Show my bookings'\n"
            response += "• 'Analyze my expenses'\n"
            response += "• 'Recommend destinations'\n"
            response += "• 'Altitude safety tips'\n"
            response += "• 'Emergency contacts'\n"
            response += "• 'Travel planning guide'\n\n"
            response += "I'm here to help with your Nepal travel experience!"
            return response
            
        except Exception as e:
            return "🤖 **TrekNepal AI Assistant:**\n\nI'm here to help with your Nepal travel experience! Ask me about:\n• Your bookings and trips\n• Travel expenses and budgets\n• Destination recommendations\n• Altitude safety and health\n• Emergency information\n• Travel planning tips"

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
                return JsonResponse({
                    'success': False,
                    'error': 'Message cannot be empty'
                })
            
            # Initialize AI assistant with current user
            ai_assistant = TrekNepalAI(request.user)
            
            # Process message and get intelligent response
            ai_response = ai_assistant.process_query(user_message)
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
                'timestamp': timezone.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST method allowed'
    })