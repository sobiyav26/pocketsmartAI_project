from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_user
from app.database import get_db

router=APIRouter()
templates=Jinja2Templates(directory="app/templates")

@router.get("/",response_class=HTMLResponse)
def index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@router.get("/login",response_class=HTMLResponse)
def login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register",response_class=HTMLResponse)
def register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

@router.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request,user=Depends(get_current_user)):
    with get_db() as db:
        count=db.execute("SELECT COUNT(*) c FROM recommendations WHERE user_id=?",(user["id"],)).fetchone()["c"]
    return templates.TemplateResponse("dashboard.html",{"request":request,"user":user,"count":count})

@router.get("/planner/{planner_type}",response_class=HTMLResponse)
def planner(request:Request,planner_type:str,user=Depends(get_current_user)):
    if planner_type not in {"home","party","jewelry"}: raise HTTPException(404,"Planner not found.")
    return templates.TemplateResponse("planner.html",{"request":request,"user":user,"planner_type":planner_type})

@router.get("/history-page",response_class=HTMLResponse)
def history_page(request:Request,user=Depends(get_current_user)):
    return templates.TemplateResponse("history.html",{"request":request,"user":user})
