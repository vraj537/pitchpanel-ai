from django.contrib import admin

from .models import Pitch


@admin.register(Pitch)
class PitchAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "idea_short", "created_at")
    search_fields = ("idea", "user__username", "user__email")
    readonly_fields = ("created_at",)

    def idea_short(self, obj):
        return obj.idea[:60]

    idea_short.short_description = "Idea"
