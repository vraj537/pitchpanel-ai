from django import forms
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class SignUpForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        data = self.cleaned_data
        name_parts = data["full_name"].strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        return User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password"],
            first_name=first_name,
            last_name=last_name,
        )


class PasswordResetForm(DjangoPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "you@example.com"}
        )


class SetPasswordForm(DjangoSetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"}
        )
