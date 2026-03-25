from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Q
import json, re, random
from datetime import datetime

from .models import (
    TravelPackage, Destination, Booking, Trekking, PeakClimbing,
    TravelExpense, TravelBudget, TravelWishlist, Guide
)

# ══════════════════════════════════════════════════════════
#  SYNONYM MAP  — expands user words to canonical keywords
# ══════════════════════════════════════════════════════════
SYNONYMS = {
    "trek": ["hike", "hiking", "trekking", "walk", "trail", "route"],
    "package": ["tour", "trip", "deal", "offer", "plan", "holiday", "vacation"],
    "booking": ["reservation", "booked", "appointment", "schedule", "trip"],
    "expense": ["spending", "cost", "money", "spent", "expenditure", "payment"],
    "budget": ["funds", "finance", "money", "allowance", "limit"],
    "guide": ["porter", "sherpa", "instructor", "leader", "escort"],
    "altitude": ["height", "elevation", "high", "mountain", "above sea level"],
    "sick": ["illness", "unwell", "nausea", "headache", "dizzy", "vomit", "fatigue"],
    "permit": ["permission", "pass", "entry", "license", "tims", "acap"],
    "season": ["time", "month", "weather", "climate", "when"],
    "cheap": ["affordable", "budget", "low cost", "inexpensive", "economical"],
    "expensive": ["costly", "luxury", "premium", "high end"],
    "easy": ["beginner", "simple", "gentle", "light", "basic"],
    "hard": ["difficult", "strenuous", "challenging", "tough", "advanced"],
    "short": ["quick", "brief", "few days", "weekend"],
    "long": ["extended", "many days", "weeks", "lengthy"],
}

# ══════════════════════════════════════════════════════════
#  INTENT DEFINITIONS
# ══════════════════════════════════════════════════════════
INTENTS = [
    {
        "tag": "greeting",
        "keywords": ["hello", "hi", "hey", "morning", "afternoon", "evening", "howdy", "sup", "greet"],
        "weight": 1,
    },
    {
        "tag": "goodbye",
        "keywords": ["bye", "goodbye", "see you", "take care", "later", "exit", "quit", "farewell"],
        "weight": 1,
    },
    {
        "tag": "thanks",
        "keywords": ["thank", "thanks", "appreciate", "helpful", "great help", "awesome"],
        "weight": 1,
    },
    {
        "tag": "ask_treks",
        "keywords": ["trek", "trekking", "hike", "trail", "route", "show trek", "list trek", "available trek", "all trek"],
        "weight": 2,
    },
    {
        "tag": "ask_packages",
        "keywords": ["package", "tour", "travel package", "show package", "list package", "available package", "holiday"],
        "weight": 2,
    },
    {
        "tag": "ask_peaks",
        "keywords": ["peak", "climbing", "mountain climb", "summit", "mountaineering", "peak climbing"],
        "weight": 2,
    },
    {
        "tag": "ask_bookings",
        "keywords": ["my booking", "my trip", "booked", "reservation", "booking history", "my reservation", "what i booked"],
        "weight": 3,
    },
    {
        "tag": "ask_expenses",
        "keywords": ["my expense", "how much spent", "spending", "expense tracker", "my cost", "total expense", "money spent"],
        "weight": 3,
    },
    {
        "tag": "ask_budget",
        "keywords": ["my budget", "travel budget", "budget status", "remaining budget", "budget left", "how much budget"],
        "weight": 3,
    },
    {
        "tag": "ask_wishlist",
        "keywords": ["wishlist", "wish list", "saved destination", "dream destination", "places i want"],
        "weight": 3,
    },
    {
        "tag": "ask_guides",
        "keywords": ["guide", "available guide", "show guide", "guide list", "verified guide", "who guide"],
        "weight": 2,
    },
    {
        "tag": "ask_ebc",
        "keywords": ["everest", "ebc", "base camp", "everest base camp", "khumbu", "namche"],
        "weight": 3,
    },
    {
        "tag": "ask_annapurna",
        "keywords": ["annapurna", "abc", "annapurna circuit", "thorong", "pokhara trek"],
        "weight": 3,
    },
    {
        "tag": "ask_langtang",
        "keywords": ["langtang", "langtang valley", "kyanjin", "gosaikunda"],
        "weight": 3,
    },
    {
        "tag": "ask_manaslu",
        "keywords": ["manaslu", "manaslu circuit", "manaslu trek"],
        "weight": 3,
    },
    {
        "tag": "ask_mustang",
        "keywords": ["mustang", "upper mustang", "lo manthang", "forbidden kingdom"],
        "weight": 3,
    },
    {
        "tag": "ask_altitude_sickness",
        "keywords": ["altitude sickness", "ams", "altitude safety", "mountain sick", "acclimatization",
                     "high altitude", "oxygen", "headache", "dizzy", "nausea altitude", "hace", "hape"],
        "weight": 3,
    },
    {
        "tag": "ask_best_season",
        "keywords": ["best time", "best season", "when trek", "when visit", "trekking season",
                     "weather", "monsoon", "spring", "autumn", "winter trek"],
        "weight": 2,
    },
    {
        "tag": "ask_permits",
        "keywords": ["permit", "tims", "acap", "national park", "entry fee", "permission", "pass"],
        "weight": 2,
    },
    {
        "tag": "ask_cost",
        "keywords": ["cost", "price", "how much", "expensive", "cheap", "affordable", "budget trek", "fee"],
        "weight": 2,
    },
    {
        "tag": "ask_packing",
        "keywords": ["pack", "packing", "what bring", "gear", "equipment", "carry", "bag", "essential item"],
        "weight": 2,
    },
    {
        "tag": "ask_guide_needed",
        "keywords": ["need guide", "hire guide", "solo trek", "without guide", "guide necessary", "guided"],
        "weight": 2,
    },
    {
        "tag": "ask_kathmandu",
        "keywords": ["kathmandu", "ktm", "pashupatinath", "boudhanath", "swayambhunath", "thamel", "durbar"],
        "weight": 2,
    },
    {
        "tag": "ask_pokhara",
        "keywords": ["pokhara", "phewa", "fewa", "sarangkot", "davis falls", "paragliding pokhara"],
        "weight": 2,
    },
    {
        "tag": "ask_insurance",
        "keywords": ["insurance", "helicopter rescue", "medical cover", "evacuation", "travel insurance"],
        "weight": 2,
    },
    {
        "tag": "ask_visa",
        "keywords": ["visa", "nepal visa", "visa arrival", "entry requirement", "passport nepal"],
        "weight": 2,
    },
    {
        "tag": "ask_difficulty",
        "keywords": ["easy trek", "hard trek", "difficult trek", "beginner trek", "moderate trek",
                     "strenuous", "which trek easy", "which trek hard", "trek for beginner"],
        "weight": 3,
    },
    {
        "tag": "ask_short_trek",
        "keywords": ["short trek", "quick trek", "few days trek", "3 day trek", "5 day trek",
                     "weekend trek", "1 week trek", "7 day trek"],
        "weight": 3,
    },
    {
        "tag": "ask_recommend",
        "keywords": ["recommend", "suggest", "best trek", "which trek should", "what trek",
                     "good trek", "popular trek", "top trek", "famous trek"],
        "weight": 3,
    },
    {
        "tag": "ask_food",
        "keywords": ["food", "eat", "meal", "dal bhat", "restaurant", "tea house food", "what to eat"],
        "weight": 2,
    },
    {
        "tag": "ask_transport",
        "keywords": ["transport", "flight", "bus", "how to reach", "get to", "travel to", "airport"],
        "weight": 2,
    },
    {
        "tag": "fallback",
        "keywords": [],
        "weight": 0,
    },
]

# ══════════════════════════════════════════════════════════
#  FOLLOW-UP SUGGESTIONS per intent
# ══════════════════════════════════════════════════════════
FOLLOWUPS = {
    "ask_treks":          ["What's the easiest trek?", "Show me short treks", "Trek costs?", "Do I need a guide?"],
    "ask_packages":       ["Show me treks too", "What's included in packages?", "My bookings"],
    "ask_peaks":          ["What permits do I need?", "Peak climbing cost?", "Do I need a guide?"],
    "ask_bookings":       ["My expenses", "My budget", "Show available treks"],
    "ask_expenses":       ["My budget", "My bookings", "Show packages"],
    "ask_budget":         ["My expenses", "Trek costs?", "My wishlist"],
    "ask_ebc":            ["EBC permits?", "Best season for EBC?", "EBC cost?", "Do I need a guide?"],
    "ask_annapurna":      ["Annapurna permits?", "Best season?", "Annapurna cost?"],
    "ask_langtang":       ["Langtang permits?", "Best season?", "Easy treks near Kathmandu?"],
    "ask_altitude_sickness": ["Altitude safety feature", "Best acclimatization tips", "Symptoms of AMS?"],
    "ask_best_season":    ["EBC best season?", "Annapurna best season?", "Monsoon trekking?"],
    "ask_permits":        ["TIMS card cost?", "Where to get permits?", "Trek costs?"],
    "ask_cost":           ["Cheap treks?", "Show packages", "Budget breakdown?"],
    "ask_packing":        ["Use packing list generator", "What gear for winter?", "Essential documents?"],
    "ask_recommend":      ["Easy treks?", "Short treks?", "Popular treks?", "Show all treks"],
    "ask_difficulty":     ["Show easy treks", "Show hard treks", "Trek for beginners?"],
    "ask_short_trek":     ["Show all treks", "Trek costs?", "Best season?"],
    "ask_kathmandu":      ["Pokhara info?", "How to get to EBC?", "Nepal visa?"],
    "ask_pokhara":        ["Annapurna trek?", "Kathmandu info?", "Transport to Pokhara?"],
    "greeting":           ["Show available treks", "My bookings", "Trek recommendations", "Altitude safety"],
}


# ══════════════════════════════════════════════════════════
#  STATIC KNOWLEDGE RESPONSES
# ══════════════════════════════════════════════════════════
STATIC_RESPONSES = {
    "ask_ebc": (
        "🏔️ **Everest Base Camp Trek**\n\n"
        "• Distance: ~130 km round trip\n"
        "• Duration: 12–14 days\n"
        "• Max altitude: 5,364m (EBC) / 5,545m (Kala Patthar)\n"
        "• Difficulty: Moderate–Strenuous\n"
        "• Best season: March–May, Sept–Nov\n"
        "• Permits: Sagarmatha NP entry (NPR 3,000) + TIMS card\n"
        "• Start point: Fly Kathmandu → Lukla (Tenzing-Hillary Airport)\n\n"
        "The trail passes through Namche Bazaar, Tengboche Monastery, Dingboche, and Gorak Shep before reaching Base Camp."
    ),
    "ask_annapurna": (
        "🏔️ **Annapurna Circuit / ABC Trek**\n\n"
        "• Circuit duration: 15–20 days | ABC: 10–12 days\n"
        "• Max altitude: Thorong La Pass 5,416m (Circuit) / 4,130m (ABC)\n"
        "• Difficulty: Moderate\n"
        "• Best season: March–May, Oct–Nov\n"
        "• Permits: ACAP (NPR 3,000) + TIMS card\n"
        "• Start: Besisahar (Circuit) or Nayapul/Pokhara (ABC)\n\n"
        "Annapurna Circuit is one of the world's classic treks with diverse landscapes from subtropical to alpine."
    ),
    "ask_langtang": (
        "🏔️ **Langtang Valley Trek**\n\n"
        "• Duration: 7–10 days\n"
        "• Max altitude: ~4,984m (Tserko Ri)\n"
        "• Difficulty: Moderate\n"
        "• Best season: March–May, Oct–Nov\n"
        "• Permits: Langtang NP entry (NPR 3,000) + TIMS\n"
        "• Start: Drive Kathmandu → Syabrubesi (7–8 hrs)\n\n"
        "Closest major trek to Kathmandu. Features Kyanjin Gompa, yak cheese farms, and stunning Langtang Lirung views."
    ),
    "ask_manaslu": (
        "🏔️ **Manaslu Circuit Trek**\n\n"
        "• Duration: 14–18 days\n"
        "• Max altitude: Larkya La Pass 5,160m\n"
        "• Difficulty: Strenuous\n"
        "• Best season: March–May, Sept–Nov\n"
        "• Permits: Restricted Area Permit (~USD 100) + MCAP + TIMS\n"
        "• Must trek with licensed guide (restricted area)\n\n"
        "Less crowded than EBC/Annapurna. Offers raw, authentic Himalayan experience around the world's 8th highest peak."
    ),
    "ask_mustang": (
        "🏔️ **Upper Mustang Trek**\n\n"
        "• Duration: 12–16 days\n"
        "• Max altitude: ~4,000m (Lo Manthang)\n"
        "• Difficulty: Moderate\n"
        "• Best season: May–Oct (open during monsoon!)\n"
        "• Permits: Restricted Area Permit USD 500/10 days + ACAP + TIMS\n"
        "• Must trek with licensed guide\n\n"
        "The 'Forbidden Kingdom' — ancient Tibetan culture, cave monasteries, and dramatic desert landscapes. Unique in Nepal."
    ),
    "ask_altitude_sickness": (
        "⚠️ **Altitude Sickness (AMS) Guide**\n\n"
        "**Symptoms:** Headache, nausea, dizziness, fatigue, loss of appetite, poor sleep\n\n"
        "**Prevention:**\n"
        "• Ascend slowly — max 300–500m/day above 3,000m\n"
        "• Rest day every 3rd day\n"
        "• Stay hydrated (3–4L water/day)\n"
        "• Avoid alcohol and sleeping pills\n"
        "• Consider Diamox (acetazolamide) — consult doctor\n\n"
        "**Golden Rule:** If symptoms worsen, descend immediately. Never ascend with AMS symptoms.\n\n"
        "Use our **Altitude Safety** feature for a personalized symptom checker! 🏥"
    ),
    "ask_best_season": (
        "📅 **Best Trekking Seasons in Nepal**\n\n"
        "**🌸 Spring (March–May)** — Best overall\n"
        "• Clear skies, rhododendrons blooming, warm days\n"
        "• Ideal for EBC, Annapurna, all major treks\n\n"
        "**🍂 Autumn (Sept–Nov)** — Most popular\n"
        "• Crystal clear views, stable weather, festive season\n"
        "• Peak season — book early!\n\n"
        "**❄️ Winter (Dec–Feb)** — For lower treks\n"
        "• Cold but clear, fewer crowds\n"
        "• Good for Langtang, Ghorepani, Poon Hill\n\n"
        "**🌧️ Monsoon (June–Aug)** — Avoid high treks\n"
        "• Leeches, landslides, poor visibility\n"
        "• Exception: Upper Mustang (rain shadow area)"
    ),
    "ask_permits": (
        "📋 **Nepal Trekking Permits**\n\n"
        "**TIMS Card** (Trekkers' Information Management System)\n"
        "• Individual: NPR 2,000 | Group: NPR 1,000\n"
        "• Required for most treks\n\n"
        "**National Park / Conservation Fees:**\n"
        "• Sagarmatha NP (EBC): NPR 3,000\n"
        "• Annapurna CA (ACAP): NPR 3,000\n"
        "• Langtang NP: NPR 3,000\n\n"
        "**Restricted Area Permits:**\n"
        "• Manaslu: USD 70–100/week\n"
        "• Upper Mustang: USD 500/10 days\n"
        "• Must have licensed guide for restricted areas\n\n"
        "Get permits at Nepal Tourism Board, Kathmandu or Pokhara."
    ),
    "ask_cost": (
        "💰 **Nepal Trekking Cost Breakdown**\n\n"
        "**Budget trekker (teahouse):** USD 30–50/day\n"
        "**Mid-range:** USD 60–100/day\n"
        "**Luxury (lodge/camping):** USD 150+/day\n\n"
        "**Typical EBC trek total:** USD 1,200–2,500\n"
        "**Annapurna Circuit:** USD 800–1,800\n\n"
        "**Includes:** Permits, accommodation, meals, guide, porter\n"
        "**Excludes:** International flights, Kathmandu hotel, gear, insurance\n\n"
        "Check our packages for all-inclusive deals! 🎒"
    ),
    "ask_packing": (
        "🎒 **Essential Packing List for Nepal Treks**\n\n"
        "**Clothing:** Moisture-wicking base layers, fleece, down jacket, waterproof shell, trekking pants, warm hat, gloves\n"
        "**Footwear:** Broken-in trekking boots, gaiters, camp sandals\n"
        "**Gear:** Trekking poles, headlamp + extra batteries, sleeping bag (-10°C for high treks)\n"
        "**Health:** First aid kit, altitude meds, water purification, sunscreen SPF50+, lip balm\n"
        "**Documents:** Passport, permits, insurance, emergency contacts\n\n"
        "💡 Use our **Packing List Generator** for a personalized list based on your trek, season, and duration!"
    ),
    "ask_guide_needed": (
        "🧭 **Do You Need a Guide?**\n\n"
        "**Required (by law):** Manaslu, Upper Mustang, Dolpo, and all restricted areas\n\n"
        "**Highly recommended:**\n"
        "• EBC, Annapurna — trail can be confusing in bad weather\n"
        "• First-time trekkers\n"
        "• Solo trekkers (safety)\n\n"
        "**Can go solo:** Langtang, Ghorepani/Poon Hill (well-marked trails)\n\n"
        "**Guide cost:** USD 25–35/day | **Porter:** USD 20–25/day\n"
        "A good guide adds safety, local knowledge, and cultural insight. Check our verified guides! 👤"
    ),
    "ask_kathmandu": (
        "🏙️ **Kathmandu — Nepal's Capital**\n\n"
        "**Must-visit sites:**\n"
        "• Pashupatinath Temple (Hindu sacred site)\n"
        "• Boudhanath Stupa (UNESCO World Heritage)\n"
        "• Swayambhunath (Monkey Temple)\n"
        "• Durbar Square (historic palace complex)\n"
        "• Thamel (tourist hub — gear shops, restaurants)\n\n"
        "**Altitude:** 1,400m — good acclimatization start\n"
        "**Getting there:** Tribhuvan International Airport (KTM)\n"
        "**Visa:** Available on arrival for most nationalities"
    ),
    "ask_pokhara": (
        "🏞️ **Pokhara — Gateway to Annapurna**\n\n"
        "**Highlights:**\n"
        "• Phewa Lake — stunning Annapurna reflection\n"
        "• Sarangkot — sunrise over Himalayas\n"
        "• Davis Falls & Gupteshwor Cave\n"
        "• Paragliding (one of the best spots in Asia!)\n"
        "• World Peace Pagoda\n\n"
        "**Altitude:** 822m\n"
        "**Getting there:** 25-min flight or 6-7 hr bus from Kathmandu\n"
        "**Trek start:** Annapurna Circuit, ABC, Ghorepani all start near Pokhara"
    ),
    "ask_insurance": (
        "🛡️ **Travel Insurance for Nepal Trekking**\n\n"
        "**Essential coverage needed:**\n"
        "• Helicopter evacuation (can cost USD 3,000–8,000!)\n"
        "• High altitude coverage (up to 6,000m for EBC)\n"
        "• Medical emergency & hospitalization\n"
        "• Trip cancellation/interruption\n\n"
        "**Recommended providers:** World Nomads, SafetyWing, Allianz\n\n"
        "⚠️ Many standard travel policies don't cover helicopter rescue above 4,000m — always check the fine print!\n"
        "Without insurance, a single helicopter rescue can cost more than your entire trip."
    ),
    "ask_visa": (
        "🛂 **Nepal Visa Information**\n\n"
        "**Visa on Arrival** available for most nationalities at KTM airport\n\n"
        "**Fees:**\n"
        "• 15 days: USD 30\n"
        "• 30 days: USD 50\n"
        "• 90 days: USD 125\n\n"
        "**Requirements:** Valid passport (6+ months), passport photo, USD cash or card\n\n"
        "**Free visa:** Indian nationals (no visa required)\n"
        "**Pre-apply:** Online at Nepal e-Visa portal to save time at airport\n\n"
        "Extensions available at Department of Immigration, Kathmandu."
    ),
    "ask_food": (
        "🍛 **Food on Nepal Treks**\n\n"
        "**Dal Bhat** — The trekker's staple! Rice + lentil soup + vegetables + pickle. Unlimited refills at most teahouses. High energy, nutritious.\n\n"
        "**Teahouse menu includes:**\n"
        "• Noodle soup, pasta, fried rice, momos (dumplings)\n"
        "• Tibetan bread, porridge, pancakes (breakfast)\n"
        "• Snickers, energy bars, instant noodles (snacks)\n\n"
        "**Prices increase with altitude** — a meal at EBC costs 3–4x Kathmandu price\n"
        "**Water:** Buy bottled or use purification tablets/filter. Avoid tap water.\n\n"
        "💡 Tip: Dal Bhat gives you unlimited energy refills — most teahouses honor this!"
    ),
    "ask_transport": (
        "🚌 **Getting Around Nepal**\n\n"
        "**To Lukla (EBC start):** Fly from KTM — 35 min, USD 180–220 one way\n"
        "**To Pokhara:** Fly 25 min (USD 80–120) or tourist bus 6–7 hrs (USD 10–15)\n"
        "**To Besisahar (Annapurna):** Bus from Kathmandu ~5 hrs\n"
        "**To Syabrubesi (Langtang):** Bus from KTM ~7–8 hrs\n\n"
        "**Within Kathmandu:** Taxi, ride-share (Pathao, inDrive), or walk in Thamel\n\n"
        "⚠️ Mountain flights are weather-dependent — always have buffer days in your itinerary!"
    ),
    "thanks": "You're welcome! 😊 Happy to help with your Nepal adventure. Is there anything else you'd like to know?",
    "goodbye": "Safe travels! 🏔️ May your trails be clear and your mountains magnificent. Come back anytime — TrekNepal AI is always here!",
}


# ══════════════════════════════════════════════════════════
#  NLP HELPERS
# ══════════════════════════════════════════════════════════
def expand_synonyms(text):
    """Replace synonym words with canonical keywords for better matching."""
    words = text.lower().split()
    expanded = list(words)
    for canonical, syns in SYNONYMS.items():
        for syn in syns:
            if syn in text.lower():
                expanded.append(canonical)
    return " ".join(expanded)


def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return expand_synonyms(text)


def extract_entities(text):
    """Extract named entities: trek names, difficulty, duration hints."""
    entities = {}
    t = text.lower()
    # Trek name detection
    trek_names = ["everest", "ebc", "annapurna", "abc", "langtang", "manaslu", "mustang",
                  "ghorepani", "poon hill", "mardi", "kanchenjunga", "dolpo", "rara"]
    for name in trek_names:
        if name in t:
            entities["trek_name"] = name
            break
    # Difficulty hints
    if any(w in t for w in ["easy", "beginner", "simple", "gentle"]):
        entities["difficulty"] = "easy"
    elif any(w in t for w in ["hard", "difficult", "strenuous", "challenging"]):
        entities["difficulty"] = "hard"
    elif any(w in t for w in ["moderate", "medium", "intermediate"]):
        entities["difficulty"] = "moderate"
    # Duration hints
    duration_match = re.search(r"(\d+)\s*day", t)
    if duration_match:
        entities["days"] = int(duration_match.group(1))
    return entities


def get_time_greeting(username=None):
    hour = datetime.now().hour
    if hour < 12:
        period = "Good morning"
    elif hour < 17:
        period = "Good afternoon"
    else:
        period = "Good evening"
    name_part = f", {username}" if username else ""
    return f"{period}{name_part}! 🏔️ Welcome to TrekNepal AI. How can I help you plan your Nepal adventure today?"


def match_intent(processed_text, last_tag=None):
    """Weighted TF-IDF-style intent matching with context awareness."""
    scores = {}
    for intent in INTENTS:
        if not intent["keywords"]:
            continue
        score = 0
        for kw in intent["keywords"]:
            if kw in processed_text:
                # Longer keyword = more specific = higher score
                score += intent["weight"] * (1 + len(kw.split()) * 0.5)
        if score > 0:
            scores[intent["tag"]] = score

    if not scores:
        return "fallback"

    best = max(scores, key=lambda t: scores[t])

    # Context boost: if follow-up question is vague, lean toward last intent's domain
    if last_tag and scores.get(best, 0) < 3:
        related = {
            "ask_ebc": ["ask_permits", "ask_cost", "ask_best_season", "ask_guide_needed"],
            "ask_annapurna": ["ask_permits", "ask_cost", "ask_best_season"],
            "ask_langtang": ["ask_permits", "ask_cost", "ask_best_season"],
        }
        if last_tag in related and best in related[last_tag]:
            return best  # keep best but context confirms it

    return best


def build_followups(tag):
    chips = FOLLOWUPS.get(tag, [])
    return chips[:4]  # max 4 chips


# ══════════════════════════════════════════════════════════
#  DB-BACKED RESPONSE BUILDERS
# ══════════════════════════════════════════════════════════
def build_trek_response(user, entities=None):
    treks = Trekking.objects.filter(is_active=True)[:8]
    if not treks.exists():
        return "No treks found in the database yet. Check back soon!"
    lines = ["🥾 **Available Treks:**\n"]
    for t in treks:
        price_str = f" | NPR {t.price:,}" if t.price else ""
        lines.append(f"• **{t.title}** — {t.difficulty} | {t.duration}{price_str}")
    return "\n".join(lines)


def build_package_response(user, entities=None):
    packages = TravelPackage.objects.all()[:6]
    if not packages.exists():
        return "No travel packages available right now. Please check back soon!"
    lines = ["📦 **Available Travel Packages:**\n"]
    for p in packages:
        price_str = f" | NPR {p.price:,}" if p.price else ""
        dur = getattr(p, 'duration', 'N/A')
        lines.append(f"• **{p.title}** — {dur}{price_str}")
    return "\n".join(lines)


def build_peak_response(user, entities=None):
    peaks = PeakClimbing.objects.filter(is_active=True)[:6]
    if not peaks.exists():
        return "No peak climbing packages found currently."
    lines = ["⛰️ **Peak Climbing Options:**\n"]
    for p in peaks:
        price_str = f" | NPR {p.price:,}" if p.price else ""
        lines.append(f"• **{p.title}** — {p.height}m{price_str}")
    return "\n".join(lines)


def build_booking_response(user):
    if not user.is_authenticated:
        return "Please log in to view your bookings. 🔐"
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')[:5]
    if not bookings.exists():
        return "You have no bookings yet. Browse our treks and packages to get started! 🎒"
    lines = [f"📋 **Your Recent Bookings:**\n"]
    for b in bookings:
        name = b.travel_package.title if b.travel_package else "Custom Booking"
        date = b.booking_date.strftime('%b %d, %Y')
        lines.append(f"• **{name}** — {b.status} | {date}")
    return "\n".join(lines)


def build_expense_response(user):
    if not user.is_authenticated:
        return "Please log in to view your expenses. 🔐"
    expenses = TravelExpense.objects.filter(user=user)
    if not expenses.exists():
        return "No expenses tracked yet. Use the Expense Tracker to log your travel spending! 💸"
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    lines = [f"💸 **Your Expense Summary:**\n", f"• Total spent: **NPR {total:,.2f}**\n"]
    by_cat = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')[:5]
    for cat in by_cat:
        cat_name = cat.get('category__name') or 'Uncategorized'
        lines.append(f"• {cat_name}: NPR {cat['total']:,.2f}")
    return "\n".join(lines)


def build_budget_response(user):
    if not user.is_authenticated:
        return "Please log in to view your budget. 🔐"
    budgets = TravelBudget.objects.filter(user=user)
    if not budgets.exists():
        return "No budget set yet. Set up a travel budget to track your spending! 📊"
    lines = ["📊 **Your Travel Budgets:**\n"]
    for b in budgets:
        total = b.total_budget
        spent = b.spent_amount()
        remaining = b.remaining_budget()
        lines.append(f"• **{b.title}** ({b.destination}): {b.currency} {total:,.0f} total | {b.currency} {spent:,.0f} spent | **{b.currency} {remaining:,.0f} remaining**")
    return "\n".join(lines)


def build_wishlist_response(user):
    if not user.is_authenticated:
        return "Please log in to view your wishlist. 🔐"
    wishlist = TravelWishlist.objects.filter(user=user)[:8]
    if not wishlist.exists():
        return "Your wishlist is empty. Start adding dream destinations! ✨"
    lines = ["✨ **Your Wishlist:**\n"]
    for w in wishlist:
        dest = getattr(w, 'destination', None) or getattr(w, 'trek', None) or str(w)
        lines.append(f"• {dest}")
    return "\n".join(lines)


def build_guide_response(user, entities=None):
    guides = Guide.objects.filter(is_verified=True)[:6] if hasattr(Guide, 'is_verified') else Guide.objects.all()[:6]
    if not guides.exists():
        return "No verified guides available right now."
    lines = ["👤 **Verified Guides:**\n"]
    for g in guides:
        exp = getattr(g, 'experience_years', 'N/A')
        langs = getattr(g, 'languages', '')
        lang_str = f" | {langs}" if langs else ""
        lines.append(f"• **{g.user.get_full_name() or g.user.username}** — {exp} yrs experience{lang_str}")
    return "\n".join(lines)


def build_difficulty_response(user, entities=None):
    treks = Trekking.objects.filter(is_active=True)
    if not treks.exists():
        return "No trek data available yet."
    diff_filter = entities.get("difficulty") if entities else None
    if diff_filter:
        filtered = [t for t in treks if diff_filter.lower() in t.difficulty.lower()]
        label = diff_filter.capitalize()
    else:
        filtered = list(treks)
        label = "All"
    if not filtered:
        return f"No {diff_filter} treks found in the database."
    lines = [f"🥾 **{label} Treks:**\n"]
    for t in filtered[:8]:
        lines.append(f"• **{t.title}** — {t.difficulty} | {t.duration}")
    return "\n".join(lines)


def build_short_trek_response(user, entities=None):
    treks = Trekking.objects.filter(is_active=True)
    max_days = entities.get("days", 7) if entities else 7
    short = []
    for t in treks:
        # duration is a CharField like "14 days" or "14"
        dur_str = re.sub(r"[^\d]", "", str(t.duration))
        try:
            if dur_str and int(dur_str) <= max_days:
                short.append(t)
        except ValueError:
            pass
    if not short:
        return f"No treks found under {max_days} days in the database. Try browsing all treks!"
    lines = [f"⚡ **Short Treks (≤{max_days} days):**\n"]
    for t in short[:6]:
        lines.append(f"• **{t.title}** — {t.duration} | {t.difficulty}")
    return "\n".join(lines)


def build_recommend_response(user, entities=None):
    treks = Trekking.objects.filter(is_active=True)[:5]
    if not treks.exists():
        return "No treks in the database yet. Check back soon!"
    lines = ["🌟 **Top Recommended Treks:**\n"]
    for t in treks:
        lines.append(f"• **{t.title}** — {t.difficulty} | {t.duration}")
    lines.append("\nUse our **Trek Fitness Matcher** for personalized recommendations based on your fitness level! 🎯")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
#  MAIN RESPONSE DISPATCHER
# ══════════════════════════════════════════════════════════
def get_response(tag, user, entities=None, last_tag=None):
    # DB-backed intents
    db_handlers = {
        "ask_treks":      lambda: build_trek_response(user, entities),
        "ask_packages":   lambda: build_package_response(user, entities),
        "ask_peaks":      lambda: build_peak_response(user, entities),
        "ask_bookings":   lambda: build_booking_response(user),
        "ask_expenses":   lambda: build_expense_response(user),
        "ask_budget":     lambda: build_budget_response(user),
        "ask_wishlist":   lambda: build_wishlist_response(user),
        "ask_guides":     lambda: build_guide_response(user, entities),
        "ask_difficulty": lambda: build_difficulty_response(user, entities),
        "ask_short_trek": lambda: build_short_trek_response(user, entities),
        "ask_recommend":  lambda: build_recommend_response(user, entities),
    }
    if tag in db_handlers:
        return db_handlers[tag]()

    # Static knowledge intents
    if tag in STATIC_RESPONSES:
        return STATIC_RESPONSES[tag]

    # Greeting — personalized
    if tag == "greeting":
        username = user.username if user.is_authenticated else None
        return get_time_greeting(username)

    # Fallback
    return (
        "🤔 I'm not sure about that one. Here are some things I can help with:\n\n"
        "• Available treks & packages\n"
        "• EBC, Annapurna, Langtang, Manaslu, Mustang info\n"
        "• Permits, costs, best seasons\n"
        "• Altitude sickness & safety\n"
        "• Your bookings, expenses & budget\n"
        "• Packing tips & guide recommendations\n\n"
        "Try asking something like: *'Tell me about EBC trek'* or *'What permits do I need?'*"
    )


# ══════════════════════════════════════════════════════════
#  VIEWS
# ══════════════════════════════════════════════════════════
@login_required
def chatbot_interface(request):
    return render(request, 'chatbot/interface.html')


@login_required
@csrf_exempt
def chatbot_message(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Empty message'})

        # Session context
        last_tag = request.session.get('chatbot_last_tag', None)

        # NLP pipeline
        processed = preprocess(user_message)
        entities = extract_entities(user_message)
        tag = match_intent(processed, last_tag=last_tag)

        # Store context for next turn
        request.session['chatbot_last_tag'] = tag

        # Build response
        response_text = get_response(tag, request.user, entities=entities, last_tag=last_tag)
        followups = build_followups(tag)

        return JsonResponse({
            'success': True,
            'response': response_text,
            'intent': tag,
            'followups': followups,
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
