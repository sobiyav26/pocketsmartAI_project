import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.dependencies import get_current_user
from app.schemas import HomeRequest, PartyRequest
from app.config import get_settings
from app.database import get_db
from app.recommendations import home_fallback, party_fallback, jewelry_fallback, _link
from app.gemini import generate_with_gemini

router = APIRouter()

def save_result(user_id, planner_type, request_data, result):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO recommendations(user_id,planner_type,request_json,result_json) VALUES(?,?,?,?)",
            (user_id,planner_type,json.dumps(request_data),json.dumps(result))
        )
        return cur.lastrowid

def prompt_for(domain, request_data):
    return f"""You are PocketSmart AI, a budget-aware recommendation assistant.
Return ONLY valid JSON, without markdown.
Domain: {domain}
User request:
{json.dumps(request_data, ensure_ascii=False)}
Use Indian rupees. Never claim live prices, inventory, ratings or availability.
Create budget allocations and useful search-oriented recommendations.
Use exactly these keys:
{{"title":"string","summary":"string","budget":number,
"allocations":[{{"category":"string","amount":number}}],
"recommendations":[{{"category":"string","name":"string","estimated_price":number,
"platform":"Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO","search_query":"string","why":"string"}}],
"assumptions":["string"]}}
Keep recommendations within the stated budget where practical."""

def normalize(result):
    required = ["title","summary","budget","allocations","recommendations"]
    if not all(k in result for k in required):
        raise ValueError("Incomplete AI response.")
    result["assumptions"] = result.get("assumptions", [])
    for r in result["recommendations"]:
        r["url"] = r.get("url") or _link(r.get("platform","Amazon"), r.get("search_query",r.get("name","")))
    return result

def generate(domain, request_data, fallback):
    settings = get_settings()
    if settings.use_mock_ai:
        out = fallback(); out["source_mode"]="mock"; return out
    try:
        out = normalize(generate_with_gemini(prompt_for(domain,request_data)))
        out["source_mode"]="gemini"
        return out
    except Exception:
        out = fallback(); out["source_mode"]="fallback"; return out

@router.post("/generate-home")
def generate_home(payload: HomeRequest, user=Depends(get_current_user)):
    out = generate("home interior",payload.model_dump(),lambda:home_fallback(payload))
    rid = save_result(user["id"],"home",payload.model_dump(),out)
    return {"id":rid,"planner_type":"home",**out}

@router.post("/generate-party")
def generate_party(payload: PartyRequest, user=Depends(get_current_user)):
    out = generate("party planning",payload.model_dump(),lambda:party_fallback(payload))
    rid = save_result(user["id"],"party",payload.model_dump(),out)
    return {"id":rid,"planner_type":"party",**out}

@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form(...),
    notes: str = Form(""),
    outfit: UploadFile | None = File(default=None),
    user=Depends(get_current_user),
):
    if budget <= 0:
        raise HTTPException(status_code=422,detail="Budget must be greater than zero.")
    image_bytes = None
    mime = None
    if outfit:
        if not outfit.content_type or not outfit.content_type.startswith("image/"):
            raise HTTPException(status_code=400,detail="Outfit file must be an image.")
        image_bytes = await outfit.read()
        if len(image_bytes) > get_settings().max_image_mb * 1024 * 1024:
            raise HTTPException(status_code=413,detail="Image is too large.")
        mime = outfit.content_type
    request_data = {"budget":budget,"occasion":occasion,"style":style,"notes":notes,"image_attached":bool(image_bytes)}
    settings = get_settings()
    if settings.use_mock_ai or not settings.gemini_api_key:
        out = jewelry_fallback(budget,occasion,style,bool(image_bytes))
        out["source_mode"]="mock" if settings.use_mock_ai else "fallback"
    else:
        try:
            out = normalize(generate_with_gemini(prompt_for("jewelry recommendation",request_data),image_bytes,mime))
            out["source_mode"]="gemini"
        except Exception:
            out = jewelry_fallback(budget,occasion,style,bool(image_bytes))
            out["source_mode"]="fallback"
    rid = save_result(user["id"],"jewelry",request_data,out)
    return {"id":rid,"planner_type":"jewelry",**out}

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id:int,user=Depends(get_current_user)):
    with get_db() as db:
        row=db.execute("SELECT * FROM recommendations WHERE id=? AND user_id=?",(recommendation_id,user["id"])).fetchone()
    if not row: raise HTTPException(status_code=404,detail="Recommendation not found.")
    return {"id":row["id"],"planner_type":row["planner_type"],"request":json.loads(row["request_json"]),
            "result":json.loads(row["result_json"]),"created_at":row["created_at"]}
