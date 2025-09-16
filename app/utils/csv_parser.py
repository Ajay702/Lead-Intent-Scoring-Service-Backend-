from io import StringIO
import pandas as pd
from typing import List, Dict

REQUIRED_COLUMNS = [
    "name", "role", "company", "industry", "location", "linkedin_bio"
]

def parse_leads_csv(file_bytes: bytes) -> List[Dict]:
    s = file_bytes.decode('utf-8', errors='ignore')
    df = pd.read_csv(StringIO(s))
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df[REQUIRED_COLUMNS].fillna("")
    leads = df.to_dict(orient='records')
    return leads
