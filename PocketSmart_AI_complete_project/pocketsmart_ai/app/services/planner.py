from app.services.fallback import home_fallback, party_fallback, jewelry_fallback
from app.services.gemini import generate


def make_recommendation(planner_type: str, data: dict, image_bytes: bytes | None = None, image_mime: str | None = None) -> dict:
    ai = generate(planner_type, data, image_bytes, image_mime)
    if ai:
        return ai
    if planner_type == "home":
        return home_fallback(data)
    if planner_type == "party":
        return party_fallback(data)
    return jewelry_fallback(data)
