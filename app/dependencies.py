from fastapi import Cookie, HTTPException, status
from app.auth import decode_access_token
from app.database import get_db

def get_current_user(access_token: str | None = Cookie(default=None)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    user_id = decode_access_token(access_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session.")
    with get_db() as db:
        user = db.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return dict(user)
