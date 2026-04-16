from app import db
from datetime import datetime

class Threat(db.Model):

    __tablename__ = "threats"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(50))

    threat_type = db.Column(db.String(100))

    anomaly_score = db.Column(db.Float)

    risk_score = db.Column(db.Float)

    severity = db.Column(db.String(20))

    status = db.Column(db.String(20), default="Active")

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)