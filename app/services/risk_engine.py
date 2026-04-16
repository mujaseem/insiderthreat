def calculate_risk(df):

    # Calculate risk score using weighted factors
    df["risk_score"] = (
        abs(df["global_score"]) * 5 +
        abs(df["user_score"]) * 5 +
        df["failed_login_attempts"] * 0.5 +
        df["data_downloaded_mb"] * 0.01
    )

    # Function to classify risk level
    def classify(score):
        if score > 8:
            return "High"
        elif score > 4:
            return "Medium"
        else:
            return "Low"

    # Apply classification
    df["risk_level"] = df["risk_score"].apply(classify)

    return df