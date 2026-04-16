def generate_explanation(log):

    reasons = []

    if log.session_duration > 300:
        reasons.append("Unusually long session duration detected")

    if log.files_accessed > 100:
        reasons.append("Accessed unusually high number of files")

    if log.commands_executed > 50:
        reasons.append("High number of system commands executed")

    if log.data_downloaded_mb > 500:
        reasons.append("Large volume of data downloaded")

    if log.failed_login_attempts > 3:
        reasons.append("Multiple failed login attempts")

    if not reasons:
        reasons.append("Minor behavioral deviation detected")

    return reasons