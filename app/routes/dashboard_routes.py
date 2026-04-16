import hashlib
import json
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from flask import send_file
from io import BytesIO
from reportlab.pdfgen import canvas

from app.services.simulation_engine import run_detection
from app.services.blockchain_logger import blockchain_logger
from app.services.explanation_engine import generate_explanation
from app.services.prediction_engine import predict_future_risk


from app.models.threat import Threat
from app.models.alert import Alert
from app.models.log import Log
from app.models.blockchain_block import BlockchainBlock


from app import db

dashboard_bp = Blueprint("dashboard", __name__)


# =================================
# Dashboard Page
# =================================
@dashboard_bp.route("/dashboard")
@login_required
def dashboard_home():
    return render_template("dashboard/dashboard.html")


# =================================
# AI Test Route
# =================================
@dashboard_bp.route("/test_ai")
@login_required
def test_ai():
    result = run_detection()
    return jsonify(result)


# =================================
# Run AI Detection
# =================================
@dashboard_bp.route("/run_detection")
@login_required
def run_detection_route():
    result = run_detection()
    return jsonify(result)


# =================================
# Dashboard Data API
# =================================
@dashboard_bp.route("/dashboard_data")
@login_required
def dashboard_data():

    # -----------------------------
    # Recent Threats
    # -----------------------------
    recent_threats = (
        Threat.query
        .order_by(Threat.timestamp.desc())
        .limit(10)
        .all()
    )

    threats = [
        {
            "id": t.id,
            "user": t.user_id,
            "risk": t.risk_score,
            "severity": t.severity,
            "status": t.status
        }
        for t in recent_threats
    ]


    # -----------------------------
    # Recent Alerts
    # -----------------------------
    recent_alerts = (
        Alert.query
        .order_by(Alert.timestamp.desc())
        .limit(5)
        .all()
    )

    alerts = [
        {
            "id": getattr(a, "threat_id", None),
            "message": a.message,
            "severity": a.severity
        }
        for a in recent_alerts
    ]


    # -----------------------------
    # Threat Timeline (SPIKE STYLE)
    # -----------------------------
    recent_activity = (
        Threat.query
        .order_by(Threat.timestamp.desc())
        .limit(30)
        .all()
    )

    timeline_labels = []
    timeline_values = []

    for threat in reversed(recent_activity):

        if threat.timestamp:

            timeline_labels.append(
                threat.timestamp.strftime("%H:%M:%S")
            )

            # Use risk score to create spikes
            timeline_values.append(
                float(threat.risk_score) if threat.risk_score else 0
            )


    # -----------------------------
    # Threat Type Distribution
    # -----------------------------
    types = (
        db.session.query(
            Threat.threat_type,
            db.func.count(Threat.id)
        )
        .group_by(Threat.threat_type)
        .all()
    )

    type_labels = []
    type_values = []

    for t in types:
        type_labels.append(t[0])
        type_values.append(t[1])


    return jsonify({
        "threats": threats,
        "alerts": alerts,
        "timeline_labels": timeline_labels,
        "timeline_values": timeline_values,
        "type_labels": type_labels,
        "type_values": type_values
    })


# =================================
# Threat Investigation
# =================================


@dashboard_bp.route("/threat/<int:threat_id>")
@login_required
def threat_investigation(threat_id):

    threat = Threat.query.get_or_404(threat_id)

    logs = (
        Log.query
        .filter_by(user_id=threat.user_id)
        .order_by(Log.timestamp.desc())
        .limit(20)
        .all()
    )

    # AI Explanation
    explanation = generate_explanation(logs[0]) if logs else []

    # Future Risk Prediction
    prediction = predict_future_risk(logs)

    return render_template(
        "dashboard/threat_investigation.html",
        threat=threat,
        logs=logs,
        explanation=explanation,
        prediction=prediction
    )



# =================================
# Threat Analysis
# =================================
@dashboard_bp.route("/threat_analysis")
@login_required
def threat_analysis():

    logs = Log.query.order_by(Log.timestamp.desc()).limit(50).all()

    anomalies = []

    for log in logs:

        score = round(log.risk_score, 2)

        if score > 10:
            level = "High Risk"
        elif score > 5:
            level = "Suspicious"
        else:
            level = "Normal"

        anomalies.append({
            "user_id": log.user_id,
            "score": score,
            "level": level
        })

    return render_template(
        "dashboard/threat_analysis.html",
        anomalies=anomalies
    )

# =================================
# Threat Management
# =================================
@dashboard_bp.route("/threat_management")
@login_required
def threat_management():

    severity = request.args.get("severity")
    status = request.args.get("status")
    threat_type = request.args.get("type")

    query = Threat.query

    if severity and severity != "All":
        query = query.filter(Threat.severity == severity)

    if status and status != "All":
        query = query.filter(Threat.status == status)

    if threat_type and threat_type != "All":
        query = query.filter(Threat.threat_type == threat_type)

    threats = (
        query
        .order_by(Threat.timestamp.desc())
        .limit(50)
        .all()
    )

    return render_template(
        "dashboard/threat_management.html",
        threats=threats
    )


# =================================
# Update Threat Status
# =================================
@dashboard_bp.route("/update_threat/<int:id>", methods=["POST"])
@login_required
def update_threat(id):

    data = request.get_json()

    threat = Threat.query.get(id)

    if threat:
        threat.status = data.get("status", threat.status)
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False}), 404


# =================================
# Blockchain Explorer
# =================================
@dashboard_bp.route("/blockchain_logs")
@login_required
def blockchain_logs():

    blocks = BlockchainBlock.query.order_by(
        BlockchainBlock.block_index.desc()
    ).limit(50).all()

    blocks = list(reversed(blocks))

    chain = []

    for i, b in enumerate(blocks):

        calculated_hash = hashlib.sha256(
            json.dumps({
                "index": b.block_index,
                "timestamp": str(b.timestamp),
                "data": b.data,
                "previous_hash": b.previous_hash
            }, sort_keys=True).encode()
        ).hexdigest()

        verified = calculated_hash == b.hash

        if i > 0 and blocks[i - 1].hash != b.previous_hash:
            verified = False

        try:
            data_display = json.loads(b.data)
        except:
            data_display = {"event": "SYSTEM", "message": b.data}

        chain.append({
            "index": b.block_index,
            "timestamp": b.timestamp,
            "data": data_display,
            "hash": b.hash,
            "previous_hash": b.previous_hash,
            "verified": verified
        })

    return render_template(
        "dashboard/blockchain_logs.html",
        chain=chain
    )
@dashboard_bp.route("/reports")
@login_required
def reports():

    threats = Threat.query.all()

    total_threats = len(threats)

    critical = len([t for t in threats if t.severity == "High"])
    active = len([t for t in threats if t.status == "Active"])
    remediated = len([t for t in threats if t.status == "Remediated"])

    avg_risk = round(
        sum([t.risk_score for t in threats]) / total_threats, 2
    ) if total_threats else 0


    # Top risky users (recent activity)
    from datetime import datetime, timedelta

    recent_time = datetime.utcnow() - timedelta(minutes=10)

    top_users = (
        Threat.query
        .filter(Threat.timestamp >= recent_time)
        .order_by(Threat.risk_score.desc())
        .limit(5)
        .all()
    )


    return render_template(
        "dashboard/reports.html",
        total_threats=total_threats,
        critical=critical,
        active=active,
        remediated=remediated,
        avg_risk=avg_risk,
        top_users=top_users
    )
@dashboard_bp.route("/reports/download")
@login_required
def download_report():

    threats = Threat.query.all()

    total_threats = len(threats)
    critical = len([t for t in threats if t.severity == "High"])
    active = len([t for t in threats if t.status == "Active"])
    remediated = len([t for t in threats if t.status == "Remediated"])

    avg_risk = round(
        sum([t.risk_score for t in threats]) / total_threats, 2
    ) if total_threats else 0

    # Top Risky Users
    from datetime import datetime, timedelta

    recent_time = datetime.utcnow() - timedelta(minutes=10)

    top_users = (
         Threat.query
         .filter(Threat.timestamp >= recent_time)
         .order_by(Threat.risk_score.desc())
         .limit(5)
        .all()
      )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "SOC INCIDENT REPORT")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 740, f"Total Threats: {total_threats}")
    pdf.drawString(100, 720, f"Critical Threats: {critical}")
    pdf.drawString(100, 700, f"Active Threats: {active}")
    pdf.drawString(100, 680, f"Remediated Threats: {remediated}")
    pdf.drawString(100, 660, f"Average Risk Score: {avg_risk}")

    # Top Risky Users Section
    pdf.drawString(100, 630, "Top Risky Users:")

    y = 610
    for t in top_users:
        pdf.drawString(
            120,
            y,
            f"{t.user_id}  |  Risk: {round(t.risk_score,2)}  |  {t.threat_type}"
        )
        y -= 20

    pdf.drawString(100, 520, "Generated by AI Behavioral SOC Platform")

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="SOC_INCIDENT_REPORT.pdf",
        mimetype="application/pdf"
    )