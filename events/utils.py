import os
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Image
from datetime import datetime
from PIL import Image as PILImage

def generate_ticket_qr(ticket):
    """Generate QR code for ticket verification"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Include ticket verification URL in QR
    verification_url = f"{settings.SITE_URL}/events/verify-ticket/{ticket.ticket_id}"
    qr.add_data(verification_url)
    qr.make(fit=True)

    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    
    # Create unique filename
    filename = f'ticket_qr_{ticket.ticket_id}.png'
    
    # Save to ticket model
    ticket.qr_code.save(filename, File(buffer), save=True)
    
    return ticket.qr_code.url

def generate_ticket_pdf(ticket):
    """Generate PDF ticket with event details and QR code"""
    buffer = BytesIO()
    
    # Create PDF
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # Keep track of dimensions
    
    # Add event banner if exists
    if ticket.ticket_type.event.banner_image:
        banner_path = ticket.ticket_type.event.banner_image.path
        pdf.drawImage(banner_path, 50, height - 250, width=500, height=200)
    
    # Add event details
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(50, height - 300, ticket.ticket_type.event.title)
    
    pdf.setFont("Helvetica", 14)
    # Date and time
    event_datetime = ticket.ticket_type.event.start_date.strftime("%B %d, %Y at %I:%M %p")
    pdf.drawString(50, height - 330, f"Date: {event_datetime}")
    
    # Venue
    pdf.drawString(50, height - 360, f"Venue: {ticket.ticket_type.event.venue}")
    pdf.drawString(50, height - 390, f"Address: {ticket.ticket_type.event.address}")
    
    # Ticket details
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 430, f"Ticket Type: {ticket.ticket_type.name}")
    
    # Ticket ID
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 460, f"Ticket ID: {ticket.ticket_id}")
    
    # Add QR code
    if ticket.qr_code:
        qr_image = PILImage.open(ticket.qr_code)
        qr_image = qr_image.resize((150, 150))  # Resize QR code
        pdf.drawImage(ticket.qr_code.path, 50, height - 650, width=150, height=150)
    
    # Add footer
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 50, "This ticket is valid for one-time use only.")
    pdf.drawString(50, 30, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pdf.save()
    buffer.seek(0)
    return buffer

def send_ticket_email(ticket):
    """Send email with PDF ticket attachment"""
    subject = f'Your Ticket for {ticket.ticket_type.event.title}'
    
    # Prepare email context
    context = {
        'ticket': ticket,
        'event': ticket.ticket_type.event,
        'verification_url': f"{settings.SITE_URL}/events/verify-ticket/{ticket.ticket_id}"
    }
    
    # Render email body from template
    email_body = render_to_string('events/emails/ticket_email.html', context)
    
    # Create email
    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[ticket.purchaser.email],
    )
    email.content_subtype = "html"  # Set email format to HTML
    
    # Generate and attach PDF ticket
    pdf_buffer = generate_ticket_pdf(ticket)
    email.attach(
        f'ticket_{ticket.ticket_id}.pdf',
        pdf_buffer.getvalue(),
        'application/pdf'
    )
    
    # Send email
    email.send()