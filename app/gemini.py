import base64
import json
import re
import requests
from app.config import get_settings

def _extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise

def generate_with_gemini(prompt: str, image_bytes: bytes | None = None, mime_type: str | None = None) -> dict:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    parts = [{"text": prompt}]
    if image_bytes:
        parts.append({"inline_data":{"mime_type":mime_type or "image/jpeg","data":base64.b64encode(image_bytes).decode("utf-8")}})
    url = f"{settings.gemini_api_base}/models/{settings.gemini_model}:generateContent"
    response = requests.post(
        url, params={"key":settings.gemini_api_key},
        json={
            "contents":[{"role":"user","parts":parts}],
            "generationConfig":{"temperature":0.35,"responseMimeType":"application/json"}
        }, timeout=60
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")
    text = "".join(p.get("text","") for p in candidates[0].get("content",{}).get("parts",[]) if p.get("text"))
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return _extract_json(text)
