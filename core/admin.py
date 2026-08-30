from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "created_at")
    search_fields = ("first_name", "last_name", "email", "message")
    readonly_fields = ("created_at",)
