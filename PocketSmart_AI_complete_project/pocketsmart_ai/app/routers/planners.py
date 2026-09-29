import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.config import settings
from app.database import db
from app.schemas import HomeRequest, PartyRequest, RecommendationResponse
from app.security import get_current_user
from app.services.planner import make_recommendation
from app.services.gemini import analyze_outfit

router = APIRouter(prefix="/api", tags=["planners"])
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def save_history(user_id: int, planner_type: str, request_data: dict, result: dict) -> int:
    with db() as conn:
        cur = conn.execute("INSERT INTO recommendations(user_id,planner_type,request_json,result_json) VALUES(?,?,?,?)", (user_id, planner_type, json.dumps(request_data), json.dumps(result)))
        return cur.lastrowid

@router.post("/generate-home", response_model=RecommendationResponse)
def generate_home(data: HomeRequest, user=Depends(get_current_user)):
    result = make_recommendation("home", data.model_dump())
    save_history(user.id, "home", data.model_dump(), result)
    return result

@router.post("/generate-party", response_model=RecommendationResponse)
def generate_party(data: PartyRequest, user=Depends(get_current_user)):
    result = make_recommendation("party", data.model_dump())
    save_history(user.id, "party", data.model_dump(), result)
    return result

@router.post("/generate-jewelry", response_model=RecommendationResponse)
async def generate_jewelry(
    budget: float = Form(..., gt=0),
    currency: str = Form("INR"),
    occasion: str = Form("Special Occasion"),
    style: str = Form("Elegant"),
    outfit_notes: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user=Depends(get_current_user),
):
    image_bytes = None
    image_analysis = None
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, "Outfit image must be JPG, PNG, or WebP")
        image_bytes = await outfit_image.read()
        if len(image_bytes) > settings.max_image_mb * 1024 * 1024:
            raise HTTPException(413, f"Image must be {settings.max_image_mb} MB or smaller")
        image_analysis = analyze_outfit(image_bytes, outfit_image.content_type)
    data = {"budget":budget,"currency":currency.upper(),"occasion":occasion,"style":style,"outfit_notes":outfit_notes}
    result = make_recommendation("jewelry", data, image_bytes, outfit_image.content_type if outfit_image else None)
    if image_analysis:
        result["image_analysis"] = image_analysis
    save_history(user.id, "jewelry", data, result)
    return result

@router.get("/history")
def history(user=Depends(get_current_user)):
    with db() as conn:
        rows = conn.execute("SELECT id,planner_type,request_json,result_json,created_at FROM recommendations WHERE user_id=? ORDER BY id DESC LIMIT 50", (user.id,)).fetchall()
    return [{"id":r["id"],"planner_type":r["planner_type"],"request":json.loads(r["request_json"]),"result":json.loads(r["result_json"]),"created_at":r["created_at"]} for r in rows]

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, user=Depends(get_current_user)):
    with db() as conn:
        row = conn.execute("SELECT * FROM recommendations WHERE id=? AND user_id=?", (recommendation_id,user.id)).fetchone()
    if not row:
        raise HTTPException(404, "Recommendation not found")
    return {"id":row["id"],"planner_type":row["planner_type"],"request":json.loads(row["request_json"]),"result":json.loads(row["result_json"]),"created_at":row["created_at"]}
