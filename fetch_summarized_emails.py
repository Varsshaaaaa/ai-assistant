import os
import google.generativeai as genai
from googleapiclient.discovery import build
from gmail_auth import authenticate_gmail

# Set Gemini API Key (Replace with your actual key)
GOOGLE_GEMINI_API_KEY = "AIzaSyBncW-rF-99TmbZMCiXLrIuSiX_kv6ANbo"
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

def fetch_emails():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    # Get latest emails (last 10 emails)
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        print("📭 No emails found.")
        return

    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        snippet = msg_data.get("snippet", "")
        
        # Generate email priority using AI
        priority = classify_email_priority(subject, snippet)
        
        # Debugging: Check the summary before sending it
        print(f"Subject: {subject}, Summary: {snippet}, Priority: {priority}")
        
        emails.append({
            "subject": subject,
            "summary": snippet if snippet else "No summary available",
            "priority": priority
        })

    # Return emails to the frontend
    return {"status": "success", "emails": emails}


def classify_email_priority(subject, snippet):
    """Uses Gemini AI to classify email priority."""
    model = genai.GenerativeModel("gemini-pro")  # Choose the best available model
    prompt = f"Classify this email into one of these categories: Urgent, Follow-up, Low Priority.\n\nSubject: {subject}\nSnippet: {snippet}\n\nPriority:"
    
    # Generate classification response
    response = model.generate_content(prompt)
    
    # Log the response for debugging
    print(f"AI Response: {response.text.strip()}")

    return response.text.strip() if response.text.strip() else "Unclassified"

# API Endpoint for Fetching Emails (Flask Route or similar would be needed)
def fetch_emails_api():
    emails = fetch_emails()
    if emails:
        return {"status": "success", "emails": emails}
    else:
        return {"status": "error", "message": "No emails found."}

# Example for how this would integrate with Flask API
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/fetch-emails", methods=["GET"])
def fetch_emails_route():
    result = fetch_emails_api()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
