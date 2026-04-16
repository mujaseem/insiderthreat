from app import db
from datetime import datetime

class Log(db.Model):

    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.String(50))

    department = db.Column(db.String(50))

    session_duration = db.Column(db.Integer)

    files_accessed = db.Column(db.Integer)

    commands_executed = db.Column(db.Integer)

    data_downloaded_mb = db.Column(db.Integer)

    failed_login_attempts = db.Column(db.Integer)

    anomaly_score = db.Column(db.Float)

    risk_score = db.Column(db.Float)

    risk_level = db.Column(db.String(20))