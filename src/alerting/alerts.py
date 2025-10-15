import os
import pandas as pd

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")  # e.g., "#alerts" or channel ID

def send_slack_alert(message: str):
    """Send a message to Slack using Slack WebClient and bot token."""
    if not SLACK_BOT_TOKEN:
        print("Slack bot token not set.")
        return
    if not SLACK_CHANNEL:
        print("Slack channel not set.")
        return
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        assert response["ok"]
    except SlackApiError as e:
        print(f"Failed to send Slack alert: {e.response['error']}")

def get_alerts(df, sentiment_col="vader_compound", threshold=-0.5):
    alert_df = df[df[sentiment_col] <= threshold]
    alert_messages = []
    for _, row in alert_df.iterrows():
        text = row.get("text", "")
        entity = row.get("entity", "Unknown")
        msg = f"ALERT: Negative sentiment ({row[sentiment_col]:.2f}) detected for {entity}.\n{text}"
        alert_messages.append(msg)
    return alert_messages
# Note: Ensure you have a .env file with NEWSAPI_KEY, GNEWS_KEY, and SLACK_token and channel set.