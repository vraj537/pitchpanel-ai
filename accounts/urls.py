from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password-reset/", views.StyledPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.StyledPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.StyledPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("reset/done/", views.StyledPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
