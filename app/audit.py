import datetime

logs = []

def log_action(user, action, details):
    logs.append({
        "user": user,
        "time": str(datetime.datetime.now()),
        "action": action,
        "details": details
    })
