import csv
from io import StringIO
from typing import List
from ..models import Result


def results_to_csv(results: List[Result]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["lead_id", "name", "company", "role", "industry", "score", "intent", "reasoning"]) 
    for r in results:
        lead = r.lead
        writer.writerow([
            r.lead_id,
            lead.name,
            lead.company,
            lead.role,
            lead.industry,
            r.score,
            r.intent,
            r.reasoning.replace("\n", " ")[:1000]
        ])
    return output.getvalue()
