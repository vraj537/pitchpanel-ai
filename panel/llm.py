"""
Calls a Hugging Face-hosted instruct model 4 times with different persona
system prompts — Investor, Skeptical Customer, Competitor, and a final
Verdict — to review a startup/project idea.

Uses Hugging Face's OpenAI-compatible chat-completions router
(https://router.huggingface.co/v1/chat/completions), which works with a
free Hugging Face account + a "read" access token — no billing needed.
"""

from concurrent.futures import ThreadPoolExecutor

import requests
from django.conf import settings

HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

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


class LLMError(Exception):
    pass


def _call_hf(system_instruction: str, user_prompt: str, max_tokens: int = 350) -> str:
    token = settings.HF_API_TOKEN
    if not token:
        raise LLMError("HF_API_TOKEN is not configured on the server.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.HF_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }

    try:
        resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=45)
    except requests.RequestException as exc:
        raise LLMError(f"Could not reach Hugging Face: {exc}") from exc

    if not resp.ok:
        raise LLMError(f"Hugging Face error {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        text = ""
    return text or "(No response generated.)"


def run_panel(idea: str) -> dict:
    """Runs the 3 persona calls in parallel, then the verdict call. Returns
    a dict with keys: investor, customer, competitor, verdict."""
    idea_prompt = f'Startup / project idea:\n"""{idea.strip()}"""'

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            key: executor.submit(_call_hf, persona, idea_prompt, 350)
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
    results["verdict"] = _call_hf(VERDICT_PERSONA, verdict_prompt, 250)
    return results
