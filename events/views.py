import requests
import json
import hmac
import hashlib
import csv
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Category, Event, TicketType, Ticket, Transaction
from .forms import EventForm, TicketTypeForm
from .utils import generate_ticket_qr, send_ticket_email
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


@login_required
def organizer_dashboard(request):
    # Get all events organized by the user
    events = Event.objects.filter(organizer=request.user)
    
    # Basic analytics
    total_events = events.count()
    active_events = events.filter(status='published').count()
    total_tickets_sold = Ticket.objects.filter(
        ticket_type__event__organizer=request.user,
        payment_status='completed'
    ).count()
    
    # Revenue analytics
    total_revenue = Transaction.objects.filter(
        ticket__ticket_type__event__organizer=request.user,
        payment_status='completed'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Recent sales
    recent_sales = Transaction.objects.filter(
        ticket__ticket_type__event__organizer=request.user,
        payment_status='completed'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_events': total_events,
        'active_events': active_events,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'recent_sales': recent_sales,
        'events': events,
    }
    
    return render(request, 'events/organizer/dashboard.html', context)


@login_required
def event_analytics(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    
    # Calculate event revenue
    event_revenue = Transaction.objects.filter(
        ticket__ticket_type__event=event,
        payment_status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get tickets sold count
    tickets_sold = Ticket.objects.filter(
        ticket_type__event=event,
        payment_status='completed'
    ).count()
    
    # Calculate capacity percentage
    capacity_percentage = (
        (tickets_sold / event.max_attendees * 100)
        if event.max_attendees
        else 0
    )
    
    # Daily sales data (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_sales = Transaction.objects.filter(
        ticket__ticket_type__event=event,
        payment_status='completed',
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('date')
    
    # Prepare data for daily sales chart
    daily_sales_dates = [sale['date'].strftime('%Y-%m-%d') for sale in daily_sales]
    daily_sales_data = [float(sale['revenue']) for sale in daily_sales]
    
    # Ticket types distribution
    ticket_types_data = TicketType.objects.filter(
        event=event
    ).annotate(
        sold=Count('tickets', filter=Q(tickets__payment_status='completed'))
    ).values('name', 'sold')
    
    ticket_types_labels = [item['name'] for item in ticket_types_data]
    ticket_types_counts = [item['sold'] for item in ticket_types_data]
    
    # Get attendees list
    attendees = Ticket.objects.filter(
        ticket_type__event=event,
        payment_status='completed'
    ).select_related('purchaser', 'ticket_type').order_by('-purchase_date')
    
    context = {
        'event': event,
        'event_revenue': event_revenue,
        'tickets_sold': tickets_sold,
        'capacity_percentage': round(capacity_percentage, 1),
        'daily_sales_dates': json.dumps(daily_sales_dates),
        'daily_sales_data': json.dumps(daily_sales_data),
        'ticket_types_labels': json.dumps(ticket_types_labels),
        'ticket_types_data': json.dumps(ticket_types_counts),
        'attendees': attendees,
    }
    
    return render(request, 'events/organizer/event_analytics.html', context)

@login_required
def export_attendees(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.title}_attendees_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Ticket ID',
        'Purchase Date',
        'Attendee Name',
        'Email',
        'Ticket Type',
        'Price Paid',
        'Status'
    ])
    
    tickets = Ticket.objects.filter(
        ticket_type__event=event,
        payment_status='completed'
    ).select_related('purchaser', 'ticket_type', 'transaction')
    
    for ticket in tickets:
        writer.writerow([
            ticket.ticket_id,
            ticket.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
            ticket.purchaser.get_full_name(),
            ticket.purchaser.email,
            ticket.ticket_type.name,
            ticket.transaction.amount if hasattr(ticket, 'transaction') else 'N/A',
            'Confirmed'
        ])
    
    return response

@login_required
def manage_events(request):
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    return render(request, 'events/manage_events.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('manage_tickets', slug=event.slug)
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def edit_event(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('manage_events')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

@login_required
def event_status(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Event.STATUS_CHOICES):
            event.status = status
            event.save()
            messages.success(request, f'Event status updated to {event.get_status_display()}')
    return redirect('manage_events')


def event_list(request):
    events = Event.objects.filter(status='published').order_by('start_date')
    featured_events = events.filter(is_featured=True)
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        events = events.filter(category__slug=category_slug)

    return render(request, 'events/event_list.html', {
        'events': events,
        'featured_events': featured_events,
        'categories': categories
    })

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    ticket_types = event.ticket_types.filter(is_active=True)
    return render(request, 'events/event_detail.html', {
        'event': event,
        'ticket_types': ticket_types
    })

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(purchaser=request.user).order_by('-purchase_date')
    return render(request, 'events/my_tickets.html', {'tickets': tickets})

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, purchaser=request.user)
    return render(request, 'events/ticket_detail.html', {'ticket': ticket})


@login_required
def manage_tickets(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    
    if request.method == 'POST':
        form = TicketTypeForm(request.POST)
        if form.is_valid():
            ticket_type = form.save(commit=False)
            ticket_type.event = event
            ticket_type.save()
            messages.success(request, 'Ticket type created successfully!')
            return redirect('manage_tickets', slug=slug)
    else:
        form = TicketTypeForm()
    
    ticket_types = event.ticket_types.all()
    return render(request, 'events/manage_tickets.html', {
        'event': event,
        'form': form,
        'ticket_types': ticket_types
    })

@login_required
def edit_ticket_type(request, slug, ticket_type_id):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    ticket_type = get_object_or_404(TicketType, id=ticket_type_id, event=event)
    
    if request.method == 'POST':
        form = TicketTypeForm(request.POST, instance=ticket_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket type updated successfully!')
            return redirect('manage_tickets', slug=slug)
    else:
        form = TicketTypeForm(instance=ticket_type)
    
    return render(request, 'events/edit_ticket_type.html', {
        'event': event,
        'form': form,
        'ticket_type': ticket_type
    })

@login_required
def delete_ticket_type(request, slug, ticket_type_id):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    ticket_type = get_object_or_404(TicketType, id=ticket_type_id, event=event)
    
    if request.method == 'POST':
        ticket_type.delete()
        messages.success(request, 'Ticket type deleted successfully!')
        return redirect('manage_tickets', slug=slug)
    
    return render(request, 'events/delete_ticket_type.html', {
        'event': event,
        'ticket_type': ticket_type
    })


# Use this view for ticket verification (e.g., at event entrance)
@login_required
def verify_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    # Check if ticket is already used
    if ticket.is_used:
        messages.error(request, 'This ticket has already been used.')
        return redirect('event_detail', slug=ticket.ticket_type.event.slug)
    
    # Check if event has already passed
    if ticket.ticket_type.event.end_date < timezone.now():
        messages.error(request, 'This event has already ended.')
        return redirect('event_detail', slug=ticket.ticket_type.event.slug)
    
    # Verify ticket
    ticket.is_used = True
    ticket.save()
    
    messages.success(request, 'Ticket successfully verified!')
    return redirect('ticket_detail', ticket_id=ticket_id)


@login_required
def initiate_purchase(request, slug, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, id=ticket_type_id, event__slug=slug)
    
    if ticket_type.is_sold_out:
        return JsonResponse({'error': 'Ticket type is sold out'}, status=400)
    
    try:
        # Create pending ticket and transaction
        ticket = Ticket.objects.create(
            ticket_type=ticket_type,
            purchaser=request.user,
            payment_status='pending'
        )
        
        transaction = Transaction.objects.create(
            user=request.user,
            ticket=ticket,
            amount=ticket_type.price,
            platform_fee=ticket_type.price * Decimal('0.05'),
            payment_status='pending'
        )
        
        # Initialize Paystack transaction
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "email": request.user.email,
            "amount": int(transaction.amount * 100),  # Convert to kobo
            "reference": str(transaction.transaction_id),
            "callback_url": request.build_absolute_uri(
                reverse('verify_payment', args=[str(transaction.transaction_id)])
            ),
            "metadata": {
                "ticket_id": str(ticket.ticket_id),
                "transaction_id": str(transaction.transaction_id),
                "custom_fields": [
                    {
                        "display_name": "Event",
                        "variable_name": "event",
                        "value": ticket_type.event.title
                    },
                    {
                        "display_name": "Ticket Type",
                        "variable_name": "ticket_type",
                        "value": ticket_type.name
                    }
                ]
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status'):
            return JsonResponse({
                'status': 'success',
                'authorization_url': response_data['data']['authorization_url']
            })
        else:
            # Clean up if payment initialization fails
            transaction.delete()
            ticket.delete()
            return JsonResponse({
                'error': response_data.get('message', 'Payment initialization failed')
            }, status=400)
            
    except Exception as e:
        # Log the error for debugging
        print(f"Payment initialization error: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred while processing your request'
        }, status=400)


@login_required
def verify_payment(request, reference):
    transaction = get_object_or_404(Transaction, transaction_id=reference)
    
    # Verify payment status with Paystack
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if response_data['data']['status'] == 'success':
            # Update transaction and ticket
            transaction.payment_status = 'completed'
            transaction.payment_reference = response_data['data']['reference']
            transaction.save()
            
            ticket = transaction.ticket
            ticket.payment_status = 'completed'
            ticket.payment_reference = response_data['data']['reference']
            ticket.save()
            
            # Generate QR code and send email
            generate_ticket_qr(ticket)
            send_ticket_email(ticket)
            
            messages.success(request, 'Payment successful! Your ticket has been sent to your email.')
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
    
    messages.error(request, 'Payment verification failed.')
    return redirect('event_detail', slug=transaction.ticket.ticket_type.event.slug)

@csrf_exempt
def payment_webhook(request):
    payload = request.body
    sign = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    
    # Verify webhook signature
    computed_sign = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    
    if sign == computed_sign:
        # Process the webhook
        payload_dict = json.loads(payload)
        
        if payload_dict['event'] == 'charge.success':
            reference = payload_dict['data']['reference']
            try:
                transaction = Transaction.objects.get(transaction_id=reference)
                if transaction.payment_status != 'completed':
                    transaction.payment_status = 'completed'
                    transaction.payment_reference = reference
                    transaction.save()
                    
                    ticket = transaction.ticket
                    ticket.payment_status = 'completed'
                    ticket.payment_reference = reference
                    ticket.save()
                    
                    generate_ticket_qr(ticket)
                    send_ticket_email(ticket)
            except Transaction.DoesNotExist:
                pass
        
        return HttpResponse(status=200)
    return HttpResponse(status=400)