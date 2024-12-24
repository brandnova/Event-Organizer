from django import forms
from .models import Event, TicketType, Category

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'description', 'banner_image', 
                 'venue', 'address', 'start_date', 'end_date', 'status', 'max_attendees']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'placeholder': 'Enter event title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'rows': '4',
                'placeholder': 'Describe your event'
            }),
            'banner_image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            }),
            'venue': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'placeholder': 'Event venue'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'rows': '2',
                'placeholder': 'Full address'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40'
            }),
            'max_attendees': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'placeholder': 'Maximum number of attendees'
            })
        }

class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ['name', 'description', 'price', 'quantity_available', 
                 'sale_start_date', 'sale_end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'rows': '3'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'step': '0.01'
            }),
            'quantity_available': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40'
            }),
            'sale_start_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'type': 'datetime-local'
            }),
            'sale_end_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40',
                'type': 'datetime-local'
            })
        }
