import streamlit as st
import google.auth
from googleapiclient.discovery import build
import json

# Load Gmail API Credentials
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="AI Email Assistant", layout="wide")

# Function to fetch emails from Gmail API
def fetch_emails():
    creds = Credentials.from_authorized_user_file("credentials.json")
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    email_data = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
        snippet = msg_detail["snippet"]
        subject = "No Subject"
        
        for header in msg_detail["payload"]["headers"]:
            if header["name"] == "Subject":
                subject = header["value"]

        email_data.append({"subject": subject, "snippet": snippet})

    return email_data

# UI Title
st.title("📩 AI-Powered Email Dashboard")

# Fetch Emails
emails = fetch_emails()

# Display Emails in Dashboard
for email in emails:
    with st.expander(f"📧 {email['subject']}"):
        st.write(email["snippet"])
