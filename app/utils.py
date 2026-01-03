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


class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))


account_activation_token = AppTokenGenerator()

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
    travel_table = Table([
        ["Package", booking.travel_package.title],
        ["Destination", booking.travel_package.destination.name],
        ["Hotel", "Hotel Everest View, Nepal"],
        ["Accommodation", "Deluxe Room (Breakfast Included)"],
        ["Ticket No.", f"TNP-{booking.id}-{date.today().year}"],
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
