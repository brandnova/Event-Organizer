from django.urls import path
from . import views

urlpatterns = [
    # Event Management
    path('organizer/dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('organizer/event/<slug:slug>/analytics/', views.event_analytics, name='event_analytics'),
    path('organizer/event/<slug:slug>/export-attendees/', views.export_attendees, name='export_attendees'),
    path('events', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('events/manage/', views.manage_events, name='manage_events'),
    path('events/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('events/<slug:slug>/status/', views.event_status, name='event_status'),
    path('event/<slug:slug>/tickets/', views.manage_tickets, name='manage_tickets'),
    path('event/<slug:slug>/tickets/<int:ticket_type_id>/edit/', views.edit_ticket_type, name='edit_ticket_type'),
    path('event/<slug:slug>/tickets/<int:ticket_type_id>/delete/', views.delete_ticket_type, name='delete_ticket_type'),
    
    # Ticket Purchase
    path('event/<slug:slug>/purchase/<int:ticket_type_id>/', 
         views.initiate_purchase, name='initiate_purchase'),
    path('payment/verify/<str:reference>/', 
         views.verify_payment, name='verify_payment'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    
    # User Tickets
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),
]