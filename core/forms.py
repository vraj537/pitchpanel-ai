from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "message"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "John"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Doe"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "john@example.com"}),
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 6, "placeholder": "How can I help?"}
            ),
        }
