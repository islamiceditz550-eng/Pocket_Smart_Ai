from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db
from app.routers import auth, pages, planners
from app.security import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
init_db()
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)

@app.get("/health")
def health():
    return {"status":"ok", "service":settings.app_name, "ai_enabled":bool(settings.gemini_api_key and settings.use_gemini), "model":settings.gemini_model}

@app.get("/api/session-info")
def session_info(user=Depends(get_current_user)):
    return {"authenticated":True,"user_id":user.id,"email":user.email}

@app.get("/api/session-data")
def session_data(user=Depends(get_current_user)):
    from app.database import db
    with db() as conn:
        counts = conn.execute("SELECT planner_type, COUNT(*) count FROM recommendations WHERE user_id=? GROUP BY planner_type", (user.id,)).fetchall()
    return {"user":{"id":user.id,"email":user.email},"recommendation_counts":{r["planner_type"]:r["count"] for r in counts}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
