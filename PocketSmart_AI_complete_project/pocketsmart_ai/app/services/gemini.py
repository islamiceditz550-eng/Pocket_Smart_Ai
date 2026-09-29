import base64
import json
from typing import Any
from app.config import settings
from app.schemas import RecommendationResponse
from app.services.platforms import attach_search_links

SYSTEM = """You are PocketSmart AI, a budget planning assistant. Return practical, conservative recommendations.
Never claim that you checked live inventory, prices, ratings, or availability unless such data is explicitly supplied by a tool.
Use estimated planning amounts, keep the total within the user's budget, and prefer search targets on the named platforms.
Do not invent direct product IDs or exact current prices. Return only JSON matching the supplied schema."""


def _client():
    if not settings.gemini_api_key or not settings.use_gemini:
        return None
    try:
        from google import genai
    except ImportError:
        return None
    return genai.Client(api_key=settings.gemini_api_key)


def generate(planner_type: str, payload: dict, image_bytes: bytes | None = None, image_mime: str | None = None) -> dict | None:
    client = _client()
    if client is None:
        return None
    prompt = f"""{SYSTEM}\n\nPlanner: {planner_type}\nUser data:\n{json.dumps(payload, indent=2)}\n\nCreate 5-8 useful recommendation items and a realistic category budget breakdown. Platform must be one of Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO. Prices are estimates only."""
    contents: Any = prompt
    if image_bytes:
        contents = [
            {"text": prompt + "\nAnalyze the outfit image only for broad color palette, style/formality and visual compatibility. Do not identify the person."},
            {"inline_data": {"mime_type": image_mime or "image/jpeg", "data": base64.b64encode(image_bytes).decode("utf-8")}},
        ]
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config={
                "system_instruction": SYSTEM,
                "response_mime_type": "application/json",
                "response_schema": RecommendationResponse.model_json_schema(),
            },
        )
        data = json.loads(response.text)
        data["planner_type"] = planner_type
        data["source_mode"] = "gemini"
        data["items"] = attach_search_links(data.get("items", []))
        return RecommendationResponse.model_validate(data).model_dump()
    except Exception:
        return None


def analyze_outfit(image_bytes: bytes, image_mime: str) -> str | None:
    client = _client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                {"text":"Describe only broad outfit color palette, style/formality, and jewelry coordination ideas. Do not identify the person or infer sensitive traits."},
                {"inline_data":{"mime_type":image_mime,"data":base64.b64encode(image_bytes).decode("utf-8")}},
            ],
        )
        return response.text.strip()
    except Exception:
        return None
