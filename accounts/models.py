from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("listener", "Listener"),
        ("curator", "Curator / Admin"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="listener",
        help_text="Designates the user role for dashboard routing and access control.",
    )
    contact_number = models.CharField(max_length=20, blank=True, default="")
    bio = models.TextField(max_length=300, blank=True, default="")

    def is_curator(self):
        return self.role == "curator" or self.is_superuser

    def is_listener(self):
        return self.role == "listener"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"