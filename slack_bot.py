import requests

SLACK_BOT_TOKEN = ""
CHANNEL_ID = ""
def fetch_slack_messages():
    url = f"https://slack.com/api/conversations.history?channel={CHANNEL_ID}"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if not data.get("ok"):
        raise Exception(f"Slack API error: {data.get('error')}")

    return data.get("messages", [])
