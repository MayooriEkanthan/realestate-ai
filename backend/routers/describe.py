from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.llm import ask

router = APIRouter(prefix="/api", tags=["describe"])

SYSTEM = (
    "You write property listing descriptions for a Sri Lankan real estate platform. "
    "Use ONLY the facts the user provides. Never invent features, measurements, prices, "
    "legal status or distances. Do not promise investment returns or guarantee anything. "
    "Write in a warm, professional tone, plain text only, with no headings or bullet points."
)


class DescribeIn(BaseModel):
    details: str = Field(min_length=10, max_length=800)
    tone: str = Field(default="friendly", pattern="^(friendly|professional|luxury)$")


@router.post("/describe")
def describe(req: DescribeIn):
    prompt = (
        f"Write an attractive listing description of about 80 words, in a {req.tone} tone.\n\n"
        f"Property facts:\n{req.details}"
    )
    text = ask(prompt, system=SYSTEM).strip()
    if not text or text.startswith("Sorry, the AI service"):
        raise HTTPException(503, "The AI service is unavailable or rate-limited. Try again in a minute.")
    return {"description": text,
            "note": "AI-written draft. The agent must check every detail before publishing."}
