from typing import List, Optional
from . import db
from .models import Offer, Lead, Result

# Offer helpers

def save_offer(name: str, value_props: str, ideal_use_cases: str) -> Offer:
    offer = Offer(name=name, value_props=value_props, ideal_use_cases=ideal_use_cases)
    db.session.add(offer)
    db.session.commit()
    return offer

# Lead helpers

def bulk_insert_leads(leads: List[dict]) -> int:
    objs = [Lead(**ld) for ld in leads]
    db.session.bulk_save_objects(objs)
    db.session.commit()
    return len(objs)

def get_all_leads() -> List[Lead]:
    return Lead.query.all()

# Result helpers

def upsert_result(lead_id: int, score: int, intent: str, reasoning: str) -> Result:
    res = Result.query.filter_by(lead_id=lead_id).first()
    if res:
        res.score = score
        res.intent = intent
        res.reasoning = reasoning
    else:
        res = Result(lead_id=lead_id, score=score, intent=intent, reasoning=reasoning)
        db.session.add(res)
    db.session.commit()
    return res

def get_all_results() -> List[Result]:
    return Result.query.join(Lead).all()

