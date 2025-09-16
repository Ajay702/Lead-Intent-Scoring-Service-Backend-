from datetime import datetime
from . import db

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value_props = db.Column(db.Text, nullable=False)
    ideal_use_cases = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    linkedin_bio = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), unique=True, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    intent = db.Column(db.String(50), nullable=False)
    reasoning = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lead = db.relationship('Lead', backref=db.backref('result', uselist=False))
