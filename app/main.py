from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import init_db
from app.routes import auth,planners,history,pages
from app.dependencies import get_current_user

settings=get_settings()
app=FastAPI(title=settings.app_name,version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/static",StaticFiles(directory="app/static"),name="static")

@app.on_event("startup")
def startup():
    init_db()
    settings.upload_dir.mkdir(parents=True,exist_ok=True)

@app.get("/health")
def health():
    return {"status":"ok","service":settings.app_name,"ai_configured":bool(settings.gemini_api_key)}

@app.get("/session-info")
def session_info():
    return {"message":"Use login/register to establish a session."}

@app.get("/session-data")
def session_data(user=__import__("fastapi").Depends(get_current_user)):
    return {"user":user}

app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)
app.include_router(pages.router)
