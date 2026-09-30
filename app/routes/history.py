import json
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.database import get_db

router=APIRouter()

@router.get("/history")
def history(user=Depends(get_current_user)):
    with get_db() as db:
        rows=db.execute("SELECT id,planner_type,request_json,result_json,created_at FROM recommendations WHERE user_id=? ORDER BY id DESC LIMIT 50",(user["id"],)).fetchall()
    return {"items":[{"id":r["id"],"planner_type":r["planner_type"],"request":json.loads(r["request_json"]),
                      "result":json.loads(r["result_json"]),"created_at":r["created_at"]} for r in rows]}
