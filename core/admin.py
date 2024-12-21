from django.contrib import admin
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone')
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'meta_title', 'meta_description', 'keywords')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin')
        }),
        ('Footer', {
            'fields': ('footer_text', 'copyright_text')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id',)
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        if self.model.objects.exists():
            return False
        return True