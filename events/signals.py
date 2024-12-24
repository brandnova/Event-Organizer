from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction, Ticket
from .utils import generate_ticket_qr, send_ticket_email

@receiver(post_save, sender=Transaction)
def handle_successful_payment(sender, instance, created, **kwargs):
    if instance.payment_status == 'completed':
        ticket = instance.ticket
        if not ticket.qr_code:
            generate_ticket_qr(ticket)
        if ticket.payment_status != 'completed':
            ticket.payment_status = 'completed'
            ticket.save()
            send_ticket_email(ticket)