import os, requests
from ..utils.logging import get_logger
logger = get_logger("notifier")

def send_slack(text: str) -> bool:
    webhook = os.getenv("SLACK_WEBHOOK", "")
    if not webhook:
        logger.warning("SLACK_WEBHOOK not set; skipping Slack notification.")
        return False
    r = requests.post(webhook, json={"text": text}, timeout=15)
    logger.info(f"Slack status: {r.status_code}")
    return r.ok
