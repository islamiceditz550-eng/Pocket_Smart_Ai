from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})

@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse(request, "history.html", {"request": request})

@router.get("/planner/{planner}", response_class=HTMLResponse)
def planner_page(request: Request, planner: str):
    if planner not in {"home","party","jewelry"}:
        from fastapi import HTTPException
        raise HTTPException(404, "Planner not found")
    return templates.TemplateResponse(request, "planner.html", {"request": request, "planner": planner})

@router.get("/results/{recommendation_id}", response_class=HTMLResponse)
def results_page(request: Request, recommendation_id: int):
    return templates.TemplateResponse(request, "results.html", {"request": request, "recommendation_id": recommendation_id})
