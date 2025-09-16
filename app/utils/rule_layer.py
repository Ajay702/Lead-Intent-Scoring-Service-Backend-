from typing import Dict

DECISION_MAKER_ROLES = {"ceo", "founder", "owner", "cto", "cfo", "coo", "chief"}
SENIOR_ROLES = {"vp", "vice president", "head", "director"}
INFLUENCER_ROLES = {"manager", "lead", "senior", "principal", "architect"}

ICP_INDUSTRIES = {"saas", "software", "technology", "tech"}
ADJACENT_INDUSTRIES = {"consulting", "services", "fintech", "healthcare tech", "edtech"}
NEUTRAL_INDUSTRIES = {"finance", "healthcare", "education", "manufacturing"}

REQUIRED_FIELDS = ["name", "role", "company", "industry", "location", "linkedin_bio"]


def score_role(role: str) -> int:
    r = (role or "").lower()
    if any(k in r for k in DECISION_MAKER_ROLES):
        return 20
    if any(k in r for k in SENIOR_ROLES):
        return 15
    if any(k in r for k in INFLUENCER_ROLES):
        return 10
    return 0


def score_industry(industry: str) -> int:
    ind = (industry or "").lower()
    if ind in ICP_INDUSTRIES:
        return 20
    if ind in ADJACENT_INDUSTRIES:
        return 12
    if ind in NEUTRAL_INDUSTRIES:
        return 5
    return 0


def score_completeness(lead: Dict) -> int:
    complete = all((lead.get(f) or "").strip() for f in REQUIRED_FIELDS)
    return 10 if complete else 0


def rule_score(lead: Dict) -> int:
    return min(50, score_role(lead.get("role", "")) + score_industry(lead.get("industry", "")) + score_completeness(lead))
