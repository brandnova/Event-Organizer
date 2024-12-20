from django.db import models
from django.core.cache import cache

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='EventHub')
    site_description = models.TextField(max_length=500)
    meta_title = models.CharField(max_length=100)
    meta_description = models.TextField(max_length=300)
    keywords = models.TextField(help_text='Comma separated keywords')
    
    # Branding
    logo = models.ImageField(upload_to='site/', null=True, blank=True)
    favicon = models.ImageField(upload_to='site/', null=True, blank=True)
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # Social Links
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    # Footer Content
    footer_text = models.TextField()
    copyright_text = models.CharField(max_length=200)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear the cache when settings are updated
        cache.delete('site_settings')
