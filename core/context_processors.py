from django.core.cache import cache
from .models import SiteSettings

def site_settings(request):
    settings = cache.get('site_settings')
    if not settings:
        settings = SiteSettings.objects.first()
        if settings:
            cache.set('site_settings', settings)
    return {'site_settings': settings}