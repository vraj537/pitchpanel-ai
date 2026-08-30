from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.ai_chat_view, name="ai_chat"),
    path("submit/", views.submit_pitch, name="submit_pitch"),
    path("pitch/<int:pk>/", views.pitch_detail, name="pitch_detail"),
]
