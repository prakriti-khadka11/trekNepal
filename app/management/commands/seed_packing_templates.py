"""
Management command to seed PackingTemplate catalogue.
Run: python manage.py seed_packing_templates
"""
from django.core.management.base import BaseCommand
from app.models import PackingTemplate

# ── Item catalogue ──────────────────────────────────────────────────────────
# Format: (trip_type, season, category, name, priority, qty, per_person, notes)

ALL = 'all'
ITEMS = [
    # ── CLOTHING — all trips, all seasons ──────────────────────────────────
    ('easy', ALL, 'clothing', 'Moisture-wicking base layer (top)', 'essential', 1, True, '1 per person'),
    ('easy', ALL, 'clothing', 'Trekking pants / convertible pants', 'essential', 2, True, '2 pairs recommended'),
    ('easy', ALL, 'clothing', 'Fleece jacket or mid-layer', 'essential', 1, True, ''),
    ('easy', ALL, 'clothing', 'Waterproof rain jacket', 'essential', 1, True, 'Hardshell preferred'),
    ('easy', ALL, 'clothing', 'Trekking socks', 'essential', 4, True, '3–5 pairs per person'),
    ('easy', ALL, 'clothing', 'Quick-dry underwear', 'essential', 3, True, '3 pairs per person'),
    ('easy', ALL, 'clothing', 'Sun hat / cap', 'essential', 1, True, ''),
    ('easy', ALL, 'clothing', 'Buff / neck gaiter', 'recommended', 1, True, ''),
    ('easy', ALL, 'clothing', 'Light gloves', 'recommended', 1, True, ''),

    # ── FOOTWEAR — all trips ────────────────────────────────────────────────
    ('easy', ALL, 'footwear', 'Trekking boots (broken in)', 'essential', 1, True, 'Waterproof, ankle support'),
    ('easy', ALL, 'footwear', 'Camp sandals / flip flops', 'recommended', 1, True, ''),
    ('easy', ALL, 'footwear', 'Gaiters', 'optional', 1, True, 'For muddy or snowy trails'),

    # ── GEAR — all trips ────────────────────────────────────────────────────
    ('easy', ALL, 'gear', 'Trekking poles', 'recommended', 2, True, 'Collapsible pair'),
    ('easy', ALL, 'gear', 'Headlamp + extra batteries', 'essential', 1, True, ''),
    ('easy', ALL, 'gear', 'Daypack (20–30L)', 'essential', 1, True, 'Per person'),
    ('easy', ALL, 'gear', 'Sleeping bag liner', 'recommended', 1, False, 'Shared or individual'),
    ('easy', ALL, 'gear', 'Dry bags / waterproof stuff sacks', 'recommended', 2, False, 'For electronics & documents'),

    # ── HEALTH — all trips ──────────────────────────────────────────────────
    ('easy', ALL, 'health', 'Personal first aid kit', 'essential', 1, False, 'Bandages, antiseptic, blister pads'),
    ('easy', ALL, 'health', 'Sunscreen SPF 50+', 'essential', 1, True, 'Reapply every 2 hrs'),
    ('easy', ALL, 'health', 'Lip balm with SPF', 'essential', 1, True, ''),
    ('easy', ALL, 'health', 'Insect repellent', 'recommended', 1, True, ''),
    ('easy', ALL, 'health', 'Hand sanitizer', 'essential', 1, False, ''),
    ('easy', ALL, 'health', 'Water purification tablets / filter', 'essential', 1, False, ''),
    ('easy', ALL, 'health', 'Pain relievers (ibuprofen / paracetamol)', 'essential', 1, True, ''),
    ('easy', ALL, 'health', 'Oral rehydration salts', 'recommended', 5, True, ''),
    ('easy', ALL, 'health', 'Blister treatment kit', 'essential', 1, True, 'Moleskin, needle, antiseptic'),
    ('easy', ALL, 'health', 'Antidiarrheal medication', 'recommended', 1, True, ''),

    # ── DOCUMENTS — all trips ───────────────────────────────────────────────
    ('easy', ALL, 'documents', 'Passport (valid 6+ months)', 'essential', 1, True, 'Original + photocopy'),
    ('easy', ALL, 'documents', 'Trekking permits (TIMS, ACAP, etc.)', 'essential', 1, True, 'Check required permits'),
    ('easy', ALL, 'documents', 'Travel insurance documents', 'essential', 1, True, 'With emergency evacuation cover'),
    ('easy', ALL, 'documents', 'Emergency contact card', 'essential', 1, True, 'Laminated copy'),
    ('easy', ALL, 'documents', 'Cash (NPR) — ATMs rare on trail', 'essential', 1, True, 'Carry sufficient cash'),
    ('easy', ALL, 'documents', 'Booking confirmation printout', 'essential', 1, False, ''),

    # ── FOOD & WATER — all trips ────────────────────────────────────────────
    ('easy', ALL, 'food_water', 'Water bottles (2L total capacity)', 'essential', 2, True, 'Hydration bladder or bottles'),
    ('easy', ALL, 'food_water', 'Energy bars / trail snacks', 'essential', 5, True, 'For between meals'),
    ('easy', ALL, 'food_water', 'Electrolyte sachets', 'recommended', 5, True, ''),

    # ── ELECTRONICS — all trips ─────────────────────────────────────────────
    ('easy', ALL, 'electronics', 'Phone + charger', 'essential', 1, True, ''),
    ('easy', ALL, 'electronics', 'Power bank (10,000+ mAh)', 'essential', 1, False, 'Shared or per person'),
    ('easy', ALL, 'electronics', 'Camera', 'optional', 1, True, ''),
    ('easy', ALL, 'electronics', 'Universal adapter', 'recommended', 1, False, ''),

    # ── MODERATE TREK extras ────────────────────────────────────────────────
    ('moderate', ALL, 'health', 'Altitude sickness medication (Diamox)', 'recommended', 1, True, 'Consult doctor before use'),
    ('moderate', ALL, 'gear', 'Trekking map / compass', 'recommended', 1, False, ''),
    ('moderate', ALL, 'gear', 'Sleeping bag (-5°C rated)', 'essential', 1, True, 'For tea house stays above 3500m'),

    # ── HIGH ALTITUDE extras ────────────────────────────────────────────────
    ('high_altitude', ALL, 'clothing', 'Down jacket / heavy insulation', 'essential', 1, True, '-10°C rated minimum'),
    ('high_altitude', ALL, 'clothing', 'Thermal base layer (bottom)', 'essential', 1, True, 'Wool or synthetic'),
    ('high_altitude', ALL, 'clothing', 'Insulated gloves + liner gloves', 'essential', 1, True, 'Layered system'),
    ('high_altitude', ALL, 'clothing', 'Wool beanie', 'essential', 1, True, ''),
    ('high_altitude', ALL, 'clothing', 'Balaclava', 'essential', 1, True, ''),
    ('high_altitude', ALL, 'clothing', 'Thermal socks (extra pairs)', 'essential', 3, True, ''),
    ('high_altitude', ALL, 'gear', '4-season sleeping bag (-10°C rated)', 'essential', 1, True, 'Check temperature rating'),
    ('high_altitude', ALL, 'gear', 'Hand warmers (10+ pairs)', 'essential', 10, False, 'Chemical heat packs'),
    ('high_altitude', ALL, 'gear', 'Insulated water bottle', 'recommended', 1, True, 'Prevents freezing'),
    ('high_altitude', ALL, 'health', 'Altitude sickness medication (Diamox)', 'essential', 1, True, 'Consult doctor before use'),
    ('high_altitude', ALL, 'health', 'Pulse oximeter', 'essential', 1, False, 'Monitor SpO2 levels'),
    ('high_altitude', ALL, 'health', 'Dexamethasone (emergency)', 'recommended', 1, False, 'Carry for emergencies'),

    # ── PEAK CLIMBING extras ────────────────────────────────────────────────
    ('peak_climbing', ALL, 'climbing', 'Climbing harness', 'essential', 1, True, 'Properly fitted'),
    ('peak_climbing', ALL, 'climbing', 'Crampons (12-point)', 'essential', 1, True, 'Compatible with boots'),
    ('peak_climbing', ALL, 'climbing', 'Ice axe', 'essential', 1, True, 'Correct length for height'),
    ('peak_climbing', ALL, 'climbing', 'Climbing helmet', 'essential', 1, True, 'CE/UIAA certified'),
    ('peak_climbing', ALL, 'climbing', 'Carabiners + slings (set)', 'essential', 1, True, ''),
    ('peak_climbing', ALL, 'climbing', 'High-altitude double boots', 'essential', 1, True, 'Insulated, crampon-compatible'),
    ('peak_climbing', ALL, 'climbing', 'Ascender / jumar', 'essential', 1, True, ''),
    ('peak_climbing', ALL, 'climbing', 'Rappel device (ATC/GriGri)', 'essential', 1, True, ''),
    ('peak_climbing', ALL, 'climbing', 'Fixed rope (check if provided)', 'recommended', 1, False, ''),
    ('peak_climbing', ALL, 'climbing', 'Expedition duffel bag (120L)', 'essential', 1, True, 'For porter loads'),
    ('peak_climbing', ALL, 'clothing', 'Down suit / expedition suit', 'essential', 1, True, '-30°C rated'),
    ('peak_climbing', ALL, 'clothing', 'High-altitude mittens', 'essential', 1, True, 'Over liner gloves'),
    ('peak_climbing', ALL, 'clothing', 'Goggles (UV400)', 'essential', 1, True, 'For snow glare'),
    ('peak_climbing', ALL, 'health', 'Supplemental oxygen equipment', 'recommended', 1, False, 'For Everest / 8000m peaks'),
    ('peak_climbing', ALL, 'health', 'Gamow bag (portable altitude chamber)', 'recommended', 1, False, 'Group equipment'),

    # ── MONSOON season extras ───────────────────────────────────────────────
    ('easy', 'monsoon', 'seasonal', 'Waterproof pack cover', 'essential', 1, True, 'Fits your pack size'),
    ('easy', 'monsoon', 'seasonal', 'Waterproof dry sacks (set)', 'essential', 3, False, 'For electronics & clothes'),
    ('easy', 'monsoon', 'seasonal', 'Extra dry socks (sealed bags)', 'essential', 3, True, ''),
    ('easy', 'monsoon', 'seasonal', 'Leech socks', 'essential', 1, True, 'High-top style'),
    ('easy', 'monsoon', 'seasonal', 'Umbrella (lightweight)', 'recommended', 1, True, ''),
    ('easy', 'monsoon', 'seasonal', 'Quick-dry towel', 'recommended', 1, True, ''),
    ('moderate', 'monsoon', 'seasonal', 'Waterproof pack cover', 'essential', 1, True, ''),
    ('moderate', 'monsoon', 'seasonal', 'Leech socks', 'essential', 1, True, ''),
    ('moderate', 'monsoon', 'seasonal', 'Waterproof dry sacks (set)', 'essential', 3, False, ''),
    ('high_altitude', 'monsoon', 'seasonal', 'Waterproof pack cover', 'essential', 1, True, ''),
    ('high_altitude', 'monsoon', 'seasonal', 'Waterproof dry sacks (set)', 'essential', 3, False, ''),
    ('peak_climbing', 'monsoon', 'seasonal', 'Waterproof pack cover', 'essential', 1, True, ''),

    # ── WINTER season extras ────────────────────────────────────────────────
    ('easy', 'winter', 'seasonal', 'Hand warmers (5+ pairs)', 'essential', 5, False, ''),
    ('easy', 'winter', 'seasonal', 'Insulated water bottle', 'recommended', 1, True, 'Prevents freezing'),
    ('moderate', 'winter', 'seasonal', 'Hand warmers (10+ pairs)', 'essential', 10, False, ''),
    ('moderate', 'winter', 'seasonal', 'Insulated water bottle', 'essential', 1, True, ''),
    ('moderate', 'winter', 'clothing', 'Down jacket / heavy insulation', 'essential', 1, True, '-10°C rated'),
    ('moderate', 'winter', 'clothing', 'Thermal base layer (bottom)', 'essential', 1, True, ''),
    ('moderate', 'winter', 'clothing', 'Insulated gloves + liner gloves', 'essential', 1, True, ''),
    ('moderate', 'winter', 'clothing', 'Wool beanie', 'essential', 1, True, ''),
    ('moderate', 'winter', 'clothing', 'Balaclava', 'essential', 1, True, ''),
    ('moderate', 'winter', 'gear', '4-season sleeping bag (-10°C rated)', 'essential', 1, True, ''),

    # ── SPRING season extras ────────────────────────────────────────────────
    ('easy', 'spring', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, 'Strong UV at altitude'),
    ('moderate', 'spring', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, ''),
    ('high_altitude', 'spring', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, ''),
    ('peak_climbing', 'spring', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, ''),

    # ── AUTUMN season extras ────────────────────────────────────────────────
    ('easy', 'autumn', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, 'Best visibility season'),
    ('moderate', 'autumn', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, ''),
    ('high_altitude', 'autumn', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, ''),
    ('peak_climbing', 'autumn', 'seasonal', 'Sunglasses (UV400)', 'essential', 1, True, ''),

    # ── LONG TREK extras (8+ days) — stored as trip_type='long' ────────────
    ('moderate', ALL, 'gear', 'Travel laundry soap / sheets', 'recommended', 1, False, ''),
    ('moderate', ALL, 'gear', 'Clothesline + pegs', 'optional', 1, False, ''),
    ('moderate', ALL, 'gear', 'Journal / notebook', 'optional', 1, True, ''),
    ('high_altitude', ALL, 'gear', 'Travel laundry soap / sheets', 'recommended', 1, False, ''),
    ('high_altitude', ALL, 'health', 'Antifungal powder / cream', 'recommended', 1, True, 'For long treks'),
    ('high_altitude', ALL, 'health', 'Nail clippers', 'recommended', 1, True, ''),
    ('peak_climbing', ALL, 'health', 'Antifungal powder / cream', 'recommended', 1, True, ''),

    # ── SPECIFIC TREKS — Everest Base Camp ──────────────────────────────────
    ('high_altitude', ALL, 'destination', 'Lukla flight booking confirmation', 'essential', 1, True, 'Kathmandu–Lukla–Kathmandu'),
    ('high_altitude', ALL, 'destination', 'Sagarmatha National Park permit', 'essential', 1, True, 'Required for EBC'),
    ('high_altitude', ALL, 'destination', 'Khumbu Pasang Lhamu Rural Municipality permit', 'essential', 1, True, ''),
    ('high_altitude', ALL, 'destination', 'Sherpa guide contact details', 'essential', 1, False, ''),
    ('high_altitude', ALL, 'destination', 'Altitude acclimatization schedule', 'essential', 1, False, 'Namche rest day mandatory'),

    # ── SPECIFIC TREKS — Annapurna Circuit ──────────────────────────────────
    ('moderate', ALL, 'destination', 'ACAP permit (Annapurna Conservation Area)', 'essential', 1, True, ''),
    ('moderate', ALL, 'destination', 'TIMS card', 'essential', 1, True, 'Trekkers Information Management System'),
    ('moderate', ALL, 'destination', 'Thorong La Pass gear check', 'essential', 1, False, 'Crampons if winter'),

    # ── PEAK CLIMBING — Everest specific ────────────────────────────────────
    ('peak_climbing', ALL, 'destination', 'Expedition permit (Ministry of Tourism)', 'essential', 1, True, 'Very expensive — book early'),
    ('peak_climbing', ALL, 'destination', 'Liaison officer contact', 'essential', 1, False, 'Mandatory for 8000m peaks'),
    ('peak_climbing', ALL, 'destination', 'Base camp equipment list (tents, kitchen)', 'essential', 1, False, 'Coordinate with agency'),
    ('peak_climbing', ALL, 'destination', 'Supplemental oxygen cylinders', 'essential', 4, True, 'For 8000m peaks'),
    ('peak_climbing', ALL, 'destination', 'Satellite phone / communication device', 'essential', 1, False, ''),
]


class Command(BaseCommand):
    help = 'Seed PackingTemplate catalogue into the database'

    def handle(self, *args, **options):
        # Clear existing
        PackingTemplate.objects.all().delete()
        self.stdout.write('Cleared existing packing templates.')

        # For easy trek items, also copy to moderate/high_altitude/peak_climbing
        # so they inherit the base items
        base_types = ['easy', 'moderate', 'high_altitude', 'peak_climbing']
        created = 0

        for row in ITEMS:
            trip_type, season, category, name, priority, qty, per_person, notes = row

            # If trip_type is 'easy' and season is 'all', create for all trip types
            # (base items everyone needs)
            if trip_type == 'easy' and season == ALL and category not in ('seasonal', 'destination', 'climbing'):
                for tt in base_types:
                    PackingTemplate.objects.create(
                        trip_type=tt, season=ALL,
                        category=category, name=name,
                        priority=priority, quantity=qty,
                        per_person=per_person, notes=notes,
                    )
                    created += 1
            else:
                PackingTemplate.objects.create(
                    trip_type=trip_type,
                    season=season if season != ALL else 'all',
                    category=category, name=name,
                    priority=priority, quantity=qty,
                    per_person=per_person, notes=notes,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} packing template items.'))
