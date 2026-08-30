from django.shortcuts import render

from .faq_data import FAQS
from .forms import ContactForm


def index_view(request):
    preview = []
    for section in FAQS:
        preview.extend(section["items"])
    return render(request, "core/index.html", {"faqs_preview": preview[:4]})


def faq_view(request):
    return render(request, "core/faq.html", {"faq_sections": FAQS})


def contact_view(request):
    sent = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            sent = True
            form = ContactForm()
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form, "sent": sent})
