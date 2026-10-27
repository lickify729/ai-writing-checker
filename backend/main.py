# backend/main.py
# The FastAPI app: defines our /api/analyze endpoint.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from ai_service import analyze_writing as ai_analyze
app = FastAPI(title="AI Writing Checker API")


# --- CORS: allow the frontend (localhost:5173) to call this backend ---
# Without this, the browser blocks cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request model: what the frontend sends ---
# Pydantic validates the incoming JSON automatically.
# If the client sends wrong types or missing fields,
# FastAPI returns a 422 error BEFORE our code even runs.
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    style: Literal["academic", "professional", "casual"] = "academic"


# --- Mock response (same shape the real AI will return in Milestone 4) ---
def get_mock_feedback(style: str) -> dict:
    return {
        "summary": f"Your writing reads as {style}. Overall, the ideas come through clearly, but a few phrases could be tightened.",
        "grammar": [
            {
                "original": "the the importance of",
                "suggestion": "the importance of",
                "explanation": "Duplicated word. Remove the repeated 'the'.",
                "severity": "high",
            }
        ],
        "clarity": [
            {
                "original": "in the event that a student decides to participate",
                "suggestion": "if a student joins",
                "explanation": "Shorter and clearer. 'In the event that' is a wordy form of 'if'.",
                "severity": "medium",
            }
        ],
        "conciseness": [
            {
                "original": "It is important to note that",
                "suggestion": "Note that",
                "explanation": "Four words reduced to two without losing meaning.",
                "severity": "low",
            }
        ],
        "tone": {
            "detected": f"Mostly {style}, with minor slips",
            "consistency": "Generally consistent",
            "note": f"Aim for a steady {style} register throughout.",
        },
        "strengths": [
            "Your main point is stated clearly.",
            "Logical flow between sentences.",
        ],
    }


# --- The endpoint ---
@app.post("/api/analyze")
def analyze_writing(request: AnalyzeRequest):
    """
    Accepts writing text + style, returns structured feedback.
    For now it returns mock data. In Milestone 4 we replace
    get_mock_feedback() with a real AI API call.
    """
    # Additional validation we can't express in Pydantic:
    # reject whitespace-only input
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty or whitespace only.")

    # Call the real AI (defined in ai_service.py)
    from ai_service import analyze_writing as ai_analyze
    return ai_analyze(request.text, request.style)