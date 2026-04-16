from app import db
from datetime import datetime

class Alert(db.Model):

    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.String(255))

    severity = db.Column(db.String(20))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)