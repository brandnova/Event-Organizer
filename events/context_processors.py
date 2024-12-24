from .models import Category

def event_categories(request):
    return {
        'categories': Category.objects.all()
    }