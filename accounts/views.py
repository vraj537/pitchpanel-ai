from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import PasswordResetForm, SetPasswordForm, SignUpForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("panel:ai_chat")

    error = None
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("panel:ai_chat")
        error = next(iter(form.errors.values()))[0]
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form, "error": error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("panel:ai_chat")

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("panel:ai_chat")
        error = "Invalid email or password."

    return render(request, "accounts/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("core:index")


class StyledPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    form_class = PasswordResetForm
    success_url = reverse_lazy("accounts:password_reset_done")


class StyledPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class StyledPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class StyledPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
