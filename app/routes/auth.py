import sqlite3
from fastapi import APIRouter, HTTPException, Response
from app.schemas import RegisterRequest, LoginRequest
from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(payload: RegisterRequest, response: Response):
    with get_db() as db:
        try:
            cur = db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                             (payload.name.strip(), payload.email.lower(), hash_password(payload.password)))
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        user_id = cur.lastrowid
    response.set_cookie("access_token", create_access_token(user_id), httponly=True, samesite="lax", max_age=86400)
    return {"message":"Registration successful.","user":{"id":user_id,"name":payload.name,"email":payload.email.lower()}}

@router.post("/login")
def login(payload: LoginRequest, response: Response):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (payload.email.lower(),)).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    response.set_cookie("access_token", create_access_token(user["id"]), httponly=True, samesite="lax", max_age=86400)
    return {"message":"Login successful.","user":{"id":user["id"],"name":user["name"],"email":user["email"]}}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message":"Logged out."}
