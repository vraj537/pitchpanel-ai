import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .llm import LLMError, run_panel
from .models import Pitch


@login_required
def ai_chat_view(request):
    history = Pitch.objects.filter(user=request.user)[:30]
    return render(
        request,
        "panel/ai_chat.html",
        {"history": history, "daily_limit": settings.DAILY_PITCH_LIMIT},
    )


@login_required
@require_POST
def submit_pitch(request):
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    idea = (body.get("idea") or "").strip()
    if not idea:
        return JsonResponse({"error": "Missing 'idea' in request body."}, status=400)

    since = timezone.now() - timedelta(hours=24)
    todays_count = Pitch.objects.filter(user=request.user, created_at__gte=since).count()
    if todays_count >= settings.DAILY_PITCH_LIMIT:
        return JsonResponse(
            {
                "error": (
                    f"Daily limit reached — you can validate {settings.DAILY_PITCH_LIMIT} "
                    "ideas per 24 hours. Please try again later."
                )
            },
            status=429,
        )

    try:
        result = run_panel(idea)
    except LLMError as exc:
        return JsonResponse({"error": "Failed to validate pitch.", "detail": str(exc)}, status=500)

    pitch = Pitch.objects.create(
        user=request.user,
        idea=idea,
        investor=result["investor"],
        customer=result["customer"],
        competitor=result["competitor"],
        verdict=result["verdict"],
    )

    return JsonResponse(
        {
            "id": pitch.id,
            "investor": pitch.investor,
            "customer": pitch.customer,
            "competitor": pitch.competitor,
            "verdict": pitch.verdict,
        }
    )


@login_required
def pitch_detail(request, pk):
    pitch = get_object_or_404(Pitch, pk=pk, user=request.user)
    return JsonResponse(
        {
            "id": pitch.id,
            "idea": pitch.idea,
            "investor": pitch.investor,
            "customer": pitch.customer,
            "competitor": pitch.competitor,
            "verdict": pitch.verdict,
        }
    )
