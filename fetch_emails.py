from googleapiclient.discovery import build
from gmail_auth import authenticate_gmail

def fetch_recent_emails():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    # Fetch emails from Inbox
    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    if not messages:
        print("📭 No emails found.")
        return

    print("\n📩 Recent Emails:\n")
    for msg in messages:
        msg_id = msg["id"]
        email_data = service.users().messages().get(userId="me", id=msg_id, format="metadata").execute()
        headers = email_data["payload"]["headers"]

        # Extract sender & subject
        sender = next(h["value"] for h in headers if h["name"] == "From")
        subject = next(h["value"] for h in headers if h["name"] == "Subject")

        print(f"📌 From: {sender}\n📜 Subject: {subject}\n{'-'*40}")

# Run email fetch
if __name__ == "__main__":
    fetch_recent_emails()
