from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Event

def organizer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'slug' in kwargs:
            event = get_object_or_404(Event, slug=kwargs['slug'])
            if event.organizer != request.user:
                messages.error(request, "You don't have permission to manage this event.")
                return redirect('events:event_detail', slug=kwargs['slug'])
        return view_func(request, *args, **kwargs)
    return _wrapped_view