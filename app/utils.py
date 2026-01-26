from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import date
import os
import random


class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))


account_activation_token = AppTokenGenerator()

def get_dynamic_booking_details(booking):
    """Generate realistic booking details based on destination and package type"""
    destination = booking.travel_package.destination
    package_title = booking.travel_package.title.lower()
    location = destination.location.lower()
    
    # Hotel mapping based on destination/location
    hotel_mapping = {
        # Everest Region
        'everest': [
            'Hotel Everest View, Syangboche',
            'Yeti Mountain Home, Namche Bazaar',
            'Hotel Himalayan Lodge, Namche',
            'Everest Summit Lodge, Monjo'
        ],
        'namche': [
            'Hotel Sherpaland, Namche Bazaar',
            'Yeti Mountain Home, Namche',
            'Hotel Himalayan Lodge, Namche'
        ],
        'lukla': [
            'Hotel Himalayan Lodge, Lukla',
            'Summit Lodge, Lukla',
            'Yeti Mountain Home, Lukla'
        ],
        'jiri': [
            'Hotel Jiri View, Jiri',
            'Sherpa Lodge, Jiri',
            'Mountain Guest House, Jiri',
            'Jiri Trekking Lodge, Jiri'
        ],
        'solukhumbu': [
            'Sherpa Lodge, Solukhumbu',
            'Mountain View Hotel, Solukhumbu',
            'Everest Gateway Lodge, Solukhumbu'
        ],
        
        # Annapurna Region
        'annapurna': [
            'Hotel Himalayan Front, Pokhara',
            'Annapurna View Lodge, Ghandruk',
            'Mountain Lodge, Chomrong',
            'Himalayan Lodge, Tadapani'
        ],
        'pokhara': [
            'Hotel Himalayan Front, Pokhara',
            'Temple Tree Resort, Pokhara',
            'Hotel Barahi, Pokhara',
            'Mount Kailash Resort, Pokhara'
        ],
        'ghandruk': [
            'Annapurna View Lodge, Ghandruk',
            'Mountain Lodge, Ghandruk',
            'Himalayan Lodge, Ghandruk'
        ],
        'kaski': [
            'Hotel Mountain View, Kaski',
            'Annapurna Lodge, Kaski',
            'Himalayan Guest House, Kaski'
        ],
        
        # Langtang Region
        'langtang': [
            'Hotel Langtang View, Syabrubesi',
            'Himalayan Lodge, Langtang Village',
            'Mountain View Lodge, Kyanjin Gompa'
        ],
        'rasuwa': [
            'Langtang Gateway Lodge, Rasuwa',
            'Mountain View Hotel, Rasuwa',
            'Himalayan Lodge, Rasuwa'
        ],
        
        # Kathmandu Valley
        'kathmandu': [
            'Hotel Himalayan Heritage, Kathmandu',
            'Kathmandu Guest House, Thamel',
            'Hotel Tibet International, Kathmandu',
            'Dwarika\'s Hotel, Kathmandu'
        ],
        'bhaktapur': [
            'Heritage Hotel, Bhaktapur',
            'Traditional Lodge, Bhaktapur',
            'Bhaktapur Guest House, Bhaktapur'
        ],
        'lalitpur': [
            'Hotel Heritage, Lalitpur',
            'Patan Guest House, Lalitpur',
            'Traditional Lodge, Lalitpur'
        ],
        
        # Eastern Nepal
        'taplejung': [
            'Kanchenjunga Lodge, Taplejung',
            'Mountain View Hotel, Taplejung',
            'Himalayan Guest House, Taplejung'
        ],
        'ilam': [
            'Tea Garden Resort, Ilam',
            'Ilam Hill Station, Ilam',
            'Green Valley Lodge, Ilam'
        ],
        'dhankuta': [
            'Hill Station Lodge, Dhankuta',
            'Mountain View Hotel, Dhankuta',
            'Dhankuta Guest House, Dhankuta'
        ],
        
        # Western Nepal
        'palpa': [
            'Tansen View Hotel, Palpa',
            'Hill Station Lodge, Tansen',
            'Heritage Hotel, Palpa'
        ],
        'tansen': [
            'Tansen View Hotel, Tansen',
            'Hill Station Lodge, Tansen',
            'Heritage Hotel, Tansen'
        ],
        'mustang': [
            'Mustang Lodge, Lo Manthang',
            'Upper Mustang Hotel, Mustang',
            'Desert Lodge, Mustang'
        ],
        
        # Central Nepal
        'dolakha': [
            'Sailung Lodge, Dolakha',
            'Mountain View Hotel, Dolakha',
            'Himalayan Guest House, Dolakha'
        ],
        
        # Other Popular Destinations
        'chitwan': [
            'Jungle Safari Lodge, Chitwan',
            'Tiger Tops Jungle Lodge, Chitwan',
            'Hotel Parkland, Chitwan'
        ],
        'lumbini': [
            'Hotel Lumbini Garden, Lumbini',
            'Buddha Maya Garden Hotel, Lumbini',
            'Lumbini Village Lodge, Lumbini'
        ],
        'bandipur': [
            'Bandipur Village Resort, Bandipur',
            'Old Inn Bandipur, Bandipur',
            'Gaun Ghar Lodge, Bandipur'
        ],
        'bardiya': [
            'Jungle Safari Lodge, Bardiya',
            'Tiger Reserve Lodge, Bardiya',
            'Wildlife Resort, Bardiya'
        ],
        'koshi': [
            'Wildlife Lodge, Koshi Tappu',
            'Bird Watching Resort, Koshi',
            'Wetland Lodge, Koshi'
        ],
        'khaptad': [
            'Khaptad Lodge, Khaptad',
            'National Park Lodge, Khaptad',
            'Mountain Resort, Khaptad'
        ]
    }
    
    # Accommodation types based on package type and destination
    accommodation_mapping = {
        'luxury': [
            'Deluxe Suite (All Meals Included)',
            'Premium Room (Breakfast & Dinner)',
            'Executive Suite (Full Board)',
            'Luxury Lodge (All Inclusive)'
        ],
        'standard': [
            'Standard Room (Breakfast Included)',
            'Twin Sharing Room (Breakfast & Dinner)',
            'Mountain View Room (Half Board)',
            'Lodge Room (Breakfast Included)'
        ],
        'budget': [
            'Basic Room (Breakfast Only)',
            'Dormitory Sharing (Meals Extra)',
            'Tea House Lodge (Basic Meals)',
            'Budget Room (Breakfast Included)'
        ],
        'trekking': [
            'Tea House Lodge (Basic Meals)',
            'Mountain Lodge (Breakfast & Dinner)',
            'Trekking Lodge (Full Board)',
            'Local Guest House (Traditional Meals)'
        ]
    }
    
    # Determine hotel based on destination with improved matching
    hotel = None
    
    # First, try exact location match
    for key, hotels in hotel_mapping.items():
        if key in location.lower():
            hotel = random.choice(hotels)
            break
    
    # If no location match, try destination name match
    if not hotel:
        for key, hotels in hotel_mapping.items():
            if key in destination.name.lower():
                hotel = random.choice(hotels)
                break
    
    # If still no match, provide region-based fallback
    if not hotel:
        # Determine region and provide appropriate fallback
        if any(word in location.lower() or word in destination.name.lower() for word in ['everest', 'solukhumbu', 'khumbu', 'sagarmatha']):
            hotel = 'Sherpa Lodge, Everest Region'
        elif any(word in location.lower() or word in destination.name.lower() for word in ['annapurna', 'pokhara', 'kaski', 'ghandruk']):
            hotel = 'Mountain Lodge, Annapurna Region'
        elif any(word in location.lower() or word in destination.name.lower() for word in ['langtang', 'rasuwa', 'helambu']):
            hotel = 'Himalayan Lodge, Langtang Region'
        elif any(word in location.lower() or word in destination.name.lower() for word in ['kathmandu', 'bhaktapur', 'lalitpur', 'patan']):
            hotel = 'Heritage Hotel, Kathmandu Valley'
        elif any(word in location.lower() or word in destination.name.lower() for word in ['chitwan', 'sauraha', 'jungle', 'safari']):
            hotel = 'Jungle Lodge, Chitwan'
        elif any(word in location.lower() or word in destination.name.lower() for word in ['lumbini', 'buddha', 'kapilvastu']):
            hotel = 'Buddha Lodge, Lumbini'
        else:
            # Final fallback with location-specific naming
            hotel = f'Mountain Lodge, {destination.location}'
    
    # Determine accommodation type based on package price and type
    accommodation_type = 'standard'
    if booking.travel_package.price > 100000:  # High-end packages
        accommodation_type = 'luxury'
    elif booking.travel_package.price < 30000:  # Budget packages
        accommodation_type = 'budget'
    elif any(word in package_title for word in ['trek', 'hiking', 'base camp']):
        accommodation_type = 'trekking'
    
    accommodation = random.choice(accommodation_mapping[accommodation_type])
    
    # Generate realistic ticket number
    destination_code = destination.name[:3].upper()
    year = booking.booking_date.year
    month = booking.booking_date.month
    ticket_number = f"TNP-{destination_code}-{booking.id}-{year}{month:02d}"
    
    return {
        'hotel': hotel,
        'accommodation': accommodation,
        'ticket_number': ticket_number,
        'destination_info': {
            'name': destination.name,
            'location': destination.location,
            'country': destination.country.name if destination.country else 'Nepal'
        }
    }

def generate_booking_pdf(booking):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []
    
    # Get dynamic booking details
    dynamic_details = get_dynamic_booking_details(booking)
    
    logo_path = os.path.join(settings.BASE_DIR, "app/static/img/logo.png")
    logo = Image(logo_path, width=160, height=50)

    title = Paragraph(
        "<b>Booking Confirmation Document</b>",
        ParagraphStyle(
            name="HeaderTitle",
            fontSize=20,
            alignment=TA_CENTER,
            leading=20, 
        )
    )

    header_table = Table(
        [[logo, title]],
        colWidths=[140, 360]
    )

    header_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

    # LOGO CELL
    ("TOPPADDING", (0, 0), (0, 0), 0),
    ("BOTTOMPADDING", (0, 0), (0, 0), 0),

    # TITLE CELL  🔑 THIS MOVES TEXT UP
    ("TOPPADDING", (1, 0), (1, 0), -6),
    ("BOTTOMPADDING", (1, 0), (1, 0), 0),

    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))

    elements.append(header_table)
    elements.append(Spacer(1, 25))
    meta = Paragraph(
        f"""
        <b>Booking ID:</b> TNP-{booking.id}<br/>
        <b>Booking Date:</b> {booking.booking_date.date()}<br/>
        <b>Payment Status:</b> <font color="green"><b>PAID</b></font>
        """,
        styles["Normal"]
    )
    elements.append(meta)
    elements.append(Spacer(1, 15))
    customer_table = Table([
        ["Customer Name", booking.user.get_full_name() or booking.user.username],
        ["Email", booking.user.email],
        ["Travel Date", str(booking.travel_date)],
        ["Number of People", booking.num_people],
    ], colWidths=[150, 300])

    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(Paragraph("<b>Customer Details</b>", styles["Heading3"]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))
    
    # Use dynamic details for travel table
    travel_table = Table([
        ["Package", booking.travel_package.title],
        ["Destination", f"{dynamic_details['destination_info']['name']}, {dynamic_details['destination_info']['location']}"],
        ["Hotel", dynamic_details['hotel']],
        ["Accommodation", dynamic_details['accommodation']],
        ["Ticket No.", dynamic_details['ticket_number']],
    ], colWidths=[150, 300])

    travel_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(Paragraph("<b>Travel & Accommodation</b>", styles["Heading3"]))
    elements.append(travel_table)
    elements.append(Spacer(1, 20))
    payment_table = Table([
        ["Total Amount", f"NPR {booking.total_price}"],
        ["Payment Method", "Khalti (Demo)"],
        ["Transaction ID", booking.khalti_pidx],
    ], colWidths=[200, 250])

    payment_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))

    elements.append(Paragraph("<b>Payment Summary</b>", styles["Heading3"]))
    elements.append(payment_table)
    elements.append(Spacer(1, 30))
    footer = Paragraph(
        """
        <font size="9" color="grey">
        This is a system-generated booking confirmation.<br/>
        Developed for academic purposes only.<br/>
        © TrekNepal
        </font>
        """,
        ParagraphStyle(name="Footer", alignment=TA_CENTER)
    )
    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def send_booking_email(booking):
    pdf = generate_booking_pdf(booking)

    email = EmailMessage(
        subject="TrekNepal Booking Confirmation",
        body=(
            f"Dear {booking.user.username},\n\n"
            f"Thank you for choosing TrekNepal.\n"
            f"Please find attached your booking confirmation.\n\n"
            f"Regards,\nTrekNepal Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.user.email],
    )

    email.attach(
        f"TrekNepal_Booking_{booking.id}.pdf",
        pdf.read(),
        "application/pdf"
    )
    email.send()
