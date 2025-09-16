import os
import requests
from typing import Tuple, Dict
from ..config import Config

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

INTENT_TO_POINTS = {"high": 50, "medium": 25, "low": 5}


def _stub_ai(offer: Dict, lead: Dict) -> Tuple[int, str, str]:
    # Simple heuristic: if role score would be high and industry in ICP, call it High
    role = (lead.get("role") or "").lower()
    industry = (lead.get("industry") or "").lower()
    
    # More nuanced scoring
    is_decision_maker = any(k in role for k in ["ceo", "founder", "owner", "cto", "cfo", "coo"])
    is_influencer = any(k in role for k in ["vp", "head", "director", "manager"])
    is_target_industry = industry in {"saas", "software", "technology", "tech"}
    is_adjacent_industry = industry in {"consulting", "services", "fintech"}
    
    if is_decision_maker and is_target_industry:
        intent, points = "High", 45
    elif is_decision_maker or (is_influencer and is_target_industry):
        intent, points = "Medium", 25
    elif is_influencer or is_adjacent_industry:
        intent, points = "Medium", 15
    else:
        intent, points = "Low", 5
        
    reasoning = f"Heuristic fallback: {role} at {industry} company suggests {intent.lower()} intent."
    return points, intent, reasoning


def call_gemini(offer: Dict, lead: Dict, prompt_template: str) -> Tuple[int, str, str]:
    api_key = Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return _stub_ai(offer, lead)

    prompt = prompt_template.format(offer=offer, lead=lead)
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(
            GEMINI_API_URL,
            params={"key": api_key},
            json=payload,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        # Extract model text
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        # Expect intent like: Intent: High\nReason: xxx
        intent = "Medium"
        reasoning = text.strip()[:500]
        for label in ["High", "Medium", "Low"]:
            if label.lower() in text.lower():
                intent = label
                break
        points = INTENT_TO_POINTS.get(intent.lower(), 30)
        return points, intent, reasoning
    except Exception as e:
        # Fallback to stub
        return _stub_ai(offer, lead)
