from flask import Blueprint, request, jsonify, current_app, send_file
from io import BytesIO
import os

from . import db
from .models import Offer, Lead, Result
from .storage import save_offer, bulk_insert_leads, get_all_results
from .utils.csv_parser import parse_leads_csv
from .utils.exporter import results_to_csv
from .services.scoring import run_scoring

bp = Blueprint('api', __name__)

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@bp.route('/offer', methods=['POST'])
def add_offer():
    data = request.get_json() or {}
    required_fields = ['name', 'value_props', 'ideal_use_cases']
    
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "Missing required fields: name, value_props, ideal_use_cases"}), 400
    
    offer = save_offer(data['name'], data['value_props'], data['ideal_use_cases'])
    return jsonify({"id": offer.id}), 201

@bp.route('/leads/upload', methods=['POST'])
def upload_leads():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    
    try:
        leads = parse_leads_csv(file.read())
        count = bulk_insert_leads(leads)
        return jsonify({"inserted": count}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/score', methods=['POST'])
def score():
    offer = Offer.query.order_by(Offer.id.desc()).first()
    if not offer:
        return jsonify({"error": "No offer found. Create an offer first."}), 400
    
    prompt_path = os.path.join(current_app.root_path, 'services', 'classification_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return jsonify({"error": "Classification prompt template not found"}), 500
    
    try:
        count = run_scoring(offer, prompt_template)
        return jsonify({"processed": count}), 200
    except Exception as e:
        return jsonify({"error": f"Scoring failed: {str(e)}"}), 500

@bp.route('/results', methods=['GET'])
def results():
    try:
        results = get_all_results()
        return jsonify([
            {
                "lead_id": r.lead.id,
                "name": r.lead.name,
                "company": r.lead.company,
                "role": r.lead.role,
                "industry": r.lead.industry,
                "score": r.score,
                "intent": r.intent,
                "reasoning": r.reasoning,
            }
            for r in results
        ]), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve results: {str(e)}"}), 500

@bp.route('/results/export', methods=['GET'])
def export_results():
    try:
        results = get_all_results()
        if not results:
            return jsonify({"error": "No results to export"}), 404
        
        csv_str = results_to_csv(results)
        csv_bytes = BytesIO(csv_str.encode('utf-8'))
        csv_bytes.seek(0)
        
        return send_file(
            csv_bytes, 
            mimetype='text/csv', 
            as_attachment=True, 
            download_name='lead_scoring_results.csv'
        )
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500
