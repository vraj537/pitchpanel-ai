from django.conf import settings
from django.db import models


class Pitch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pitches")
    idea = models.TextField()
    investor = models.TextField(blank=True, default="")
    customer = models.TextField(blank=True, default="")
    competitor = models.TextField(blank=True, default="")
    verdict = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.idea[:40]}"
