from typing import Dict, List, Tuple
from ..storage import get_all_leads, upsert_result
from ..models import Offer
from ..utils.rule_layer import rule_score
from ..utils.ai_layer import call_gemini


def run_scoring(offer: Offer, prompt_template: str) -> int:
    leads = get_all_leads()
    count = 0
    for lead in leads:
        ldict = {
            "name": lead.name,
            "role": lead.role,
            "company": lead.company,
            "industry": lead.industry,
            "location": lead.location,
            "linkedin_bio": lead.linkedin_bio,
        }
        rscore = rule_score(ldict)
        offer_dict = {
            "name": offer.name,
            "value_props": offer.value_props,
            "ideal_use_cases": offer.ideal_use_cases,
        }
        ai_points, intent, reasoning = call_gemini(offer_dict, ldict, prompt_template)
        final = min(100, rscore + ai_points)
        upsert_result(lead_id=lead.id, score=final, intent=intent, reasoning=reasoning)
        count += 1
    return count
