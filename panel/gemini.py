"""
Calls the Gemini API 4 times with different persona system prompts —
Investor, Skeptical Customer, Competitor, and a final Verdict — to
review a startup/project idea. Ported from the original
api/validate-pitch.js Vercel function, using `requests` instead of fetch.

Uses GEMINI_MODEL (default: gemini-3.1-flash-lite) — the current
free-tier "lite" model, chosen for its much higher daily request quota
compared to the full Flash/Pro models, since each pitch uses 4 calls.
"""

from concurrent.futures import ThreadPoolExecutor

import requests
from django.conf import settings

PERSONAS = {
    "investor": (
        "You are a sharp, numbers-driven startup investor reviewing a pitch for possible funding.\n"
        "Evaluate market size, scalability, revenue model and realistic ROI.\n"
        "Respond in plain text (no markdown symbols like * or #), 3-5 short lines covering strengths "
        "and concerns, then end with one line: \"Verdict: Fund\" or \"Verdict: Pass\" or "
        "\"Verdict: Needs more info\"."
    ),
    "customer": (
        "You are a skeptical, price-conscious potential customer being pitched this idea.\n"
        "React honestly and in first person: would you actually pay for or use this? What doubts or "
        "objections do you have?\n"
        "Respond in plain text (no markdown symbols), 3-5 short lines, casual and honest in tone."
    ),
    "competitor": (
        "You are a rival founder building in the same space, sizing up this idea as competition.\n"
        "Mention existing alternatives, where this idea is weak or strong versus them, and how you'd "
        "beat it in the market.\n"
        "Respond in plain text (no markdown symbols), 3-5 short lines."
    ),
}

VERDICT_PERSONA = (
    "You are the moderator of an AI startup evaluation panel.\n"
    "Given the idea and the Investor, Customer and Competitor feedback, write a short overall verdict: "
    "a viability score out of 10, the single biggest strength, the single biggest risk, and one concrete "
    "next step.\n"
    "Respond in plain text (no markdown symbols), under 120 words."
)


class GeminiError(Exception):
    pass


def _call_gemini(system_instruction: str, user_prompt: str, max_tokens: int = 350) -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured on the server.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
    }

    try:
        resp = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
    except requests.RequestException as exc:
        raise GeminiError(f"Could not reach Gemini: {exc}") from exc

    if not resp.ok:
        raise GeminiError(f"Gemini error {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError, TypeError):
        text = ""
    return text or "(No response generated.)"


def run_panel(idea: str) -> dict:
    """Runs the 3 persona calls in parallel, then the verdict call. Returns
    a dict with keys: investor, customer, competitor, verdict."""
    idea_prompt = f'Startup / project idea:\n"""{idea.strip()}"""'

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            key: executor.submit(_call_gemini, persona, idea_prompt, 350)
            for key, persona in PERSONAS.items()
        }
        results = {key: future.result() for key, future in futures.items()}

    verdict_prompt = (
        f'Idea:\n"""{idea.strip()}"""\n\n'
        f'Investor feedback:\n{results["investor"]}\n\n'
        f'Customer feedback:\n{results["customer"]}\n\n'
        f'Competitor feedback:\n{results["competitor"]}\n\n'
        "Based on all three, give the final panel verdict."
    )
    results["verdict"] = _call_gemini(VERDICT_PERSONA, verdict_prompt, 250)
    return results
