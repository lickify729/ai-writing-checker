# backend/ai_service.py
# Handles all communication with the Purdue GenAI API.
# Keeping this separate from main.py means the endpoint logic
# (HTTP, CORS, validation) stays clean, and the AI logic is
# testable on its own.

import json
import os
import re
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

# Load .env from this directory so GEMMA_API_KEY is available
load_dotenv()

# --- API config (all server-side, never exposed to the browser) ---
API_URL = "https://genai.rcac.purdue.edu/api/chat/completions"
MODEL = "gemma4:26b-a4b"
TIMEOUT = 45  # seconds — the AI can take a while on longer texts


def _get_api_key() -> str:
    """Fetch the key from the environment. Fail loudly if missing."""
    key = os.getenv("GEMMA_API_KEY")
    if not key or key == "your_key_here":
        raise HTTPException(
            status_code=500,
            detail="Server is missing GEMMA_API_KEY. Check backend/.env.",
        )
    return key


def _build_system_prompt(style: str) -> str:
    """The instructions we give the AI. This shapes the whole output."""
    return f"""You are an expert writing coach. Analyze the user's writing and give
helpful, actionable feedback that helps them become a better writer — do not
just rewrite everything for them.

Target style: {style.capitalize()}.

Rules:
- Base every point on text that actually exists in what the user wrote.
  Do NOT invent errors or problems that aren't there.
- If the writing is already good in a category, return an empty list for it
  and say so in the summary. Praise good work honestly.
- Preserve the writer's intended meaning and voice.
- Treat subjective style choices as gentle suggestions, not objective rules.
  Only flag real grammatical, spelling, or punctuation errors as high severity.
- "severity" must be exactly one of: "low", "medium", "high".
  Use "high" only for real errors (grammar/spelling). "medium" for things that
  hurt clarity. "low" for optional polish.
- Each issue's "original" field must be the EXACT text copied from the input.

Return ONLY valid JSON. No markdown, no code fences, no commentary outside
the JSON. Use exactly this structure:

{{
  "summary": "1-2 sentence overall assessment",
  "grammar": [
    {{"original": "exact text", "suggestion": "fix", "explanation": "why", "severity": "low|medium|high"}}
  ],
  "clarity": [
    {{"original": "exact text", "suggestion": "fix", "explanation": "why", "severity": "low|medium|high"}}
  ],
  "conciseness": [
    {{"original": "exact text", "suggestion": "fix", "explanation": "why", "severity": "low|medium|high"}}
  ],
  "tone": {{
    "detected": "what tone it reads as",
    "consistency": "how consistent it is",
    "note": "one short remark"
  }},
  "strengths": ["thing the writer did well", "another"]
}}"""


def _build_user_prompt(text: str) -> str:
    return f"Analyze this writing and return the JSON feedback:\n\n\"\"\"{text}\"\"\""


def _extract_json(raw: str) -> dict:
    """
    LLMs sometimes wrap JSON in markdown code fences (```json ... ```)
    or add a stray sentence. This finds the first { ... } block and
    parses it. Raises HTTPException if no valid JSON is found.
    """
    # Try parsing the whole response first
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        pass

    # Fallback: find the outermost { ... } block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except (ValueError, TypeError):
            pass

    raise HTTPException(
        status_code=502,
        detail="The AI returned a response we couldn't read as JSON. Please try again.",
    )

def _safe_json(text: str) -> dict:
    import json
    return json.loads(text)


def _validate_feedback(data: dict) -> dict:
    """
    Ensure the AI returned the shape our frontend expects.
    If a section is missing or wrong, we normalize it rather than
    crashing. Better to show a partial result than an error page.
    """
    required = ["summary", "grammar", "clarity", "conciseness", "tone", "strengths"]
    for key in required:
        if key not in data:
            # Provide sane defaults for anything missing
            if key in ("grammar", "clarity", "conciseness"):
                data[key] = []
            elif key == "summary":
                data[key] = "Analysis complete."
            elif key == "tone":
                data[key] = {"detected": "unclear", "consistency": "n/a", "note": ""}
            elif key == "strengths":
                data[key] = []

    # Validate each issue list
    valid_severities = ("low", "medium", "high")
    for category in ("grammar", "clarity", "conciseness"):
        if not isinstance(data[category], list):
            data[category] = []
        cleaned = []
        for item in data[category]:
            if not isinstance(item, dict):
                continue
            issue = {
                "original": str(item.get("original", "")),
                "suggestion": str(item.get("suggestion", "")),
                "explanation": str(item.get("explanation", "")),
                "severity": str(item.get("severity", "low")).lower(),
            }
            if issue["severity"] not in valid_severities:
                issue["severity"] = "low"
            cleaned.append(issue)
        data[category] = cleaned

    # Validate tone
    tone = data.get("tone", {})
    if not isinstance(tone, dict):
        tone = {}
    data["tone"] = {
        "detected": str(tone.get("detected", "unclear")),
        "consistency": str(tone.get("consistency", "n/a")),
        "note": str(tone.get("note", "")),
    }

    # Validate strengths
    if not isinstance(data["strengths"], list):
        data["strengths"] = []
    data["strengths"] = [str(s) for s in data["strengths"] if str(s).strip()]

    return data


def analyze_writing(text: str, style: str) -> dict:
    """
    Main entry point. Sends text to the AI, returns validated feedback.
    Raises HTTPException with a user-friendly message on any failure.
    """
    api_key = _get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": _build_system_prompt(style)},
            {"role": "user", "content": _build_user_prompt(text)},
        ],
        "temperature": 0.3,  # lower = more consistent, factual output
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="The AI service took too long to respond. Please try again.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Could not reach the AI service. Check your network/VPN connection.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Unexpected error calling the AI: {type(e).__name__}")

    # --- Handle HTTP status codes from the AI service ---
    if response.status_code == 401:
        raise HTTPException(status_code=500, detail="Invalid API key. Check backend/.env.")
    if response.status_code == 429:
        raise HTTPException(status_code=429, detail="You've hit the rate limit. Please wait a moment and try again.")
    if response.status_code >= 500:
        raise HTTPException(status_code=502, detail="The AI service is having trouble. Please try again shortly.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"AI service returned an unexpected error ({response.status_code}).")

    # --- Extract the AI's text ---
    try:
        body = response.json()
        content = body["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise HTTPException(status_code=502, detail="The AI returned an empty or unexpected response. Please try again.")

    if not content or not content.strip():
        raise HTTPException(status_code=502, detail="The AI returned an empty response. Please try again.")

    # --- Parse and validate the JSON ---
    data = _extract_json(content)
    return _validate_feedback(data)