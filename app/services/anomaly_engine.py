from sklearn.ensemble import IsolationForest
import pandas as pd


class AnomalyEngine:

    def __init__(self):
        self.global_model = IsolationForest(contamination=0.05)
        self.user_models = {}

    # -------------------------------
    # Global Behavioral Model
    # -------------------------------
    def train_global(self, df):

        features = df[[
            "session_duration",
            "files_accessed",
            "commands_executed",
            "data_downloaded_mb",
            "failed_login_attempts"
        ]]

        self.global_model.fit(features)

    def detect_global(self, df):

        features = df[[
            "session_duration",
            "files_accessed",
            "commands_executed",
            "data_downloaded_mb",
            "failed_login_attempts"
        ]]

        scores = self.global_model.decision_function(features)
        preds = self.global_model.predict(features)

        df["global_score"] = scores
        df["global_anomaly"] = preds

        return df

    # -------------------------------
    # User Behavioral Model
    # -------------------------------
    def detect_user_behavior(self, df):

        user_scores = []

        for user in df["user_id"].unique():

            user_df = df[df["user_id"] == user]

            features = user_df[[
                "session_duration",
                "files_accessed",
                "commands_executed",
                "data_downloaded_mb",
                "failed_login_attempts"
            ]]

            model = IsolationForest(contamination=0.05)
            model.fit(features)

            score = model.decision_function(features)
            pred = model.predict(features)

            user_df["user_score"] = score
            user_df["user_anomaly"] = pred

            user_scores.append(user_df)

        return pd.concat(user_scores)