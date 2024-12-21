from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('attendee', 'Attendee'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='attendee')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
