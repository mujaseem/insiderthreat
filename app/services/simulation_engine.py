from app.services.log_generator import generate_logs
from app.services.anomaly_engine import AnomalyEngine
from app.services.risk_engine import calculate_risk
from app.services.blockchain_logger import blockchain_logger

from app.models.log import Log
from app.models.threat import Threat
from app.models.alert import Alert

from app import db
from datetime import datetime


# Initialize anomaly engine
engine = AnomalyEngine()


def run_detection():
    # Generate synthetic enterprise logs
    df = generate_logs(30)

    # Train anomaly detection model
    engine.train_global(df)

    # Detect global anomalies
    df = engine.detect_global(df)

    # Detect user behavior anomalies
    df = engine.detect_user_behavior(df)

    # Calculate risk score
    df = calculate_risk(df)

    # Severity counter for dashboard charts
    severity_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0
    }

    for _, row in df.iterrows():

        # -----------------------------
        # STORE LOG IN DATABASE
        # -----------------------------
        log = Log(
            user_id=row["user_id"],
            department=row["department"],
            session_duration=row["session_duration"],
            files_accessed=row["files_accessed"],
            commands_executed=row["commands_executed"],
            data_downloaded_mb=row["data_downloaded_mb"],
            failed_login_attempts=row["failed_login_attempts"],
            anomaly_score=float(row["global_score"]),
            risk_score=float(row["risk_score"]),
            risk_level=row["risk_level"]
        )

        db.session.add(log)

        # Count severity for charts
        severity_counts[row["risk_level"]] = severity_counts.get(row["risk_level"], 0) + 1

        # -----------------------------
        # CREATE THREAT + ALERT
        # -----------------------------
        if row["risk_score"] > 5:

            # Threat classification
            if row["data_downloaded_mb"] > 500:
                threat_type = "Data Exfiltration"

            elif row["failed_login_attempts"] > 5:
                threat_type = "Suspicious Login"

            elif row["commands_executed"] > 40:
                threat_type = "Privilege Abuse"

            elif row["files_accessed"] > 80:
                threat_type = "Malware Activity"

            else:
                threat_type = "Behavioral Anomaly"

            # Create threat record
            threat = Threat(
                user_id=row["user_id"],
                threat_type=threat_type,
                severity=row["risk_level"],
                risk_score=float(row["risk_score"]),
                status="Active",
                timestamp=datetime.now()
            )

            db.session.add(threat)

            # Create alert record
            alert = Alert(
                message=f"High risk activity detected for {row['user_id']}",
                severity=row["risk_level"],
                timestamp=datetime.utcnow()
            )

            db.session.add(alert)

            # -----------------------------
            # BLOCKCHAIN LOGGING
            # -----------------------------
            blockchain_logger.add_block({
                "event": "THREAT_DETECTED",
                "user": row["user_id"],
                "threat_type": threat_type,
                "risk_score": float(row["risk_score"]),
                "severity": row["risk_level"],
                "timestamp": str(datetime.utcnow())
            })

    # Commit all records
    db.session.commit()

    # -----------------------------
    # TOP RISKY USERS (Dashboard)
    # -----------------------------
    top_users = (
        df.sort_values("risk_score", ascending=False)
        .head(5)[["user_id", "risk_score"]]
        .to_dict(orient="records")
    )

    return {
        "severity": severity_counts,
        "top_users": top_users
    }