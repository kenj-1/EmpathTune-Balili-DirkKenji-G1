from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
        help_text="Required. Must be a valid and unique email address.",
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial="listener",
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Select 'Listener' for personal listening or 'Curator' for catalog management.",
    )
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+63 900 000 0000"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "contact_number")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style password fields with Bootstrap
        for field in ("password", "password_confirm"):
            if field in self.fields:
                self.fields[field].widget.attrs.update({"class": "form-control"})