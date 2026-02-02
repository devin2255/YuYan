import datetime
import os

import requests


def send_feishu_message(data):
    webhook = os.environ.get("FEISHU_WEBHOOK_URL")
    if not webhook:
        return False
    try:
        params = {"data": data, "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        headers = {"Content-Type": "application/json"}
        requests.post(url=webhook, json=params, headers=headers, timeout=0.3)
        return True
    except Exception:
        return False
