from django.contrib import admin
from django.utils.html import format_html
from .models import Event, Category, TicketType, Ticket, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_date', 'status', 'is_featured', 'tickets_sold_display')
    list_filter = ('status', 'is_featured', 'category', 'start_date')
    search_fields = ('title', 'organizer__username', 'venue')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')
    
    def tickets_sold_display(self, obj):
        return obj.tickets_sold()
    tickets_sold_display.short_description = 'Tickets Sold'

    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'slug', 'organizer', 'category', 'description')
        }),
        ('Event Details', {
            'fields': ('banner_image', 'venue', 'address', 'start_date', 'end_date')
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'max_attendees')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'quantity_available', 'remaining_quantity', 'is_active')
    list_filter = ('is_active', 'event', 'sale_start_date')
    search_fields = ('name', 'event__title')
    readonly_fields = ('remaining_quantity',)

    def remaining_quantity(self, obj):
        return obj.remaining_quantity
    remaining_quantity.short_description = 'Remaining Tickets'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'event_title', 'purchaser', 'purchase_date', 'payment_status', 'is_used')
    list_filter = ('payment_status', 'is_used', 'purchase_date')
    search_fields = ('ticket_id', 'purchaser__username', 'ticket_type__event__title')
    readonly_fields = ('ticket_id', 'qr_code_display')
    
    def event_title(self, obj):
        return obj.ticket_type.event.title
    event_title.short_description = 'Event'
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="150" height="150" />', obj.qr_code.url)
        return "No QR code generated"
    qr_code_display.short_description = 'QR Code'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'payment_reference')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')