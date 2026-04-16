def predict_future_risk(logs):

    if not logs:
        return {
            "current_risk": 0,
            "trend": "Stable",
            "predicted_risk": 0
        }

    # Latest risk
    current_risk = logs[0].risk_score

    # Calculate average past risk
    past_risks = [log.risk_score for log in logs]
    avg_risk = sum(past_risks) / len(past_risks)

    # Determine trend
    if current_risk > avg_risk:
        trend = "Increasing"
    elif current_risk < avg_risk:
        trend = "Decreasing"
    else:
        trend = "Stable"

    # Predict future risk
    predicted_risk = current_risk * 1.2 if trend == "Increasing" else current_risk * 0.9

    return {
        "current_risk": round(current_risk,2),
        "trend": trend,
        "predicted_risk": round(predicted_risk,2)
    }