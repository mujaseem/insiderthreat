import random
import pandas as pd
from datetime import datetime

departments = ["IT_Admin","Finance","Manager","HR","Developer"]

def generate_logs(n=200):

    logs = []

    for i in range(n):

        user = f"EMP{random.randint(1000,1050)}"
        dept = random.choice(departments)

        session_duration = random.randint(10,300)
        files_accessed = random.randint(1,50)
        commands_executed = random.randint(1,30)
        data_downloaded = random.randint(0,200)
        failed_logins = random.randint(0,5)

        # 🚨 Inject malicious insider behaviour (8% probability)
        if random.random() < 0.08:

            session_duration = random.randint(400,900)
            files_accessed = random.randint(200,500)
            commands_executed = random.randint(80,150)
            data_downloaded = random.randint(400,800)
            failed_logins = random.randint(5,20)

        log = {
            "timestamp": datetime.now(),
            "user_id": user,
            "department": dept,
            "session_duration": session_duration,
            "files_accessed": files_accessed,
            "commands_executed": commands_executed,
            "data_downloaded_mb": data_downloaded,
            "failed_login_attempts": failed_logins
        }

        logs.append(log)

    return pd.DataFrame(logs)