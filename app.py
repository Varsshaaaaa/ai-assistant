from flask import Flask, request, jsonify, render_template
from gmail_auth import authenticate_gmail  # Ensure you have this module for Gmail authentication
from slack_bot import fetch_slack_messages  # Ensure you have this module for Slack messages
from wp_bot import send_whatsapp_message, fetch_whatsapp_messages  # Ensure you have these functions implemented
import google.generativeai as genai
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from datetime import datetime, timedelta

# Configure Google Gemini AI
GOOGLE_GEMINI_API_KEY = "AIzaSyBncW-rF-99TmbZMCiXLrIuSiX_kv6ANbo"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

# Load the trained summarization model
MODEL_PATH = "chat_summary_model"  # Ensure this path exists
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)

app = Flask(__name__)

# In-memory storage for follow-ups and reminders (for demonstration purposes)
follow_ups = {}

scheduler = BackgroundScheduler()

def fetch_and_respond_to_whatsapp_messages():
    """Fetches WhatsApp messages, generates replies, and sends them."""
    try:
        messages = fetch_whatsapp_messages()  # Fetch messages from WhatsApp
        for message in messages:
            # Generate a smart reply
            reply = generate_smart_reply(message['text'])
            # Send the reply back to the user
            send_whatsapp_message(message['from'], reply)
            
            # Optionally, summarize the chat
            summary = summarize_chat([msg['text'] for msg in messages])
            print(f"Summary of chat: {summary}")  # Log or store the summary as needed
    except Exception as e:
        print(f"Error fetching and responding to WhatsApp messages: {str(e)}")

# Schedule the task to run every minute
scheduler.add_job(fetch_and_respond_to_whatsapp_messages, 'interval', minutes=1)
scheduler.start()

def fetch_emails():
    """Fetches latest 10 emails, classifies them using AI, and returns structured data."""
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    # Get latest 10 emails
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        return []

    classified_emails = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        snippet = msg_data.get("snippet", "")

        # Classify email using AI
        priority = classify_email_priority(subject, snippet)
        
        classified_emails.append({
            "priority": priority,
            "subject": subject,
            "snippet": snippet
        })

    return classified_emails

def classify_email_priority(subject, snippet):
    """Uses Gemini AI to classify email priority."""
    model = genai.GenerativeModel("gemini-pro")  # Choose the best available model
    prompt = f"Classify this email into one of these categories: Urgent, Follow-up, Low Priority.\n\nSubject: {subject}\nSnippet: {snippet}\n\nPriority:"
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_smart_reply(message):
    """Generates a smart reply using Gemini AI."""
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Generate a concise and polite response to this message: {message}"
    
    response = model.generate_content(prompt)
    return response.text.strip()

def summarize_chat(messages):
    """Summarizes a chat conversation using the trained T5 model."""
    inputs = tokenizer(messages, return_tensors="pt", truncation=True, max_length=512)
    summary_ids = model.generate(**inputs)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetch-emails", methods=["GET"])
def get_emails():
    try:
        emails = fetch_emails()
        return jsonify({"status": "success", "emails": emails})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/fetch-slack", methods=["GET"])
def get_slack_messages():
    try:
        messages = fetch_slack_messages()
        return jsonify({"status": "success", "messages": messages})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/send-whatsapp", methods=["POST"])
def send_wp_message():
    try:
        data = request.get_json()
        phone = data.get("phone")
        message = data.get("message")
        
        if not phone or not message:
            return jsonify({"status": "error", "message": "Missing phone or message"})
        
        send_whatsapp_message(phone, message)
        return jsonify({"status": "success", "message": "Message sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/whatsapp/smart-reply", methods=["POST"])
def whatsapp_smart_reply():
    try:
        data = request.get_json()
        message = data.get("message")
        
        if not message:
            return jsonify({"status": "error", "message": "Missing message"})
        
        reply = generate_smart_reply(message)
        return jsonify({"status": "success", "reply": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/whatsapp/summarize-chat", methods=["POST"])
def whatsapp_summarize_chat():
    try:
        data = request.get_json()
        messages = data.get("messages")
        
        if not messages:
            return jsonify({"status": "error", "message": "Missing messages"}), 400
        
        summary = summarize_chat(messages)
        return jsonify({"status": "success", "summary": summary}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/whatsapp/set-follow-up", methods=["POST"])
def whatsapp_set_follow_up():
    try:
        data = request.get_json()
        phone = data.get("phone")
        message = data.get("message")
        follow_up_time = data.get("follow_up_time")  # Expected in minutes
        
        if not phone or not message or not follow_up_time:
            return jsonify({"status": "error", "message": "Missing phone, message, or follow_up_time"})
        
        follow_up_time = int(follow_up_time)
        follow_up_datetime = datetime.now() + timedelta(minutes=follow_up_time)
        follow_ups[phone] = {"message": message, "time": follow_up_datetime}
        
        return jsonify({"status": "success", "message": f"Follow-up set for {follow_up_datetime}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/whatsapp/check-follow-ups", methods=["GET"])
def whatsapp_check_follow_ups():
    try:
        current_time = datetime.now()
        pending_follow_ups = []

        for phone, follow_up in follow_ups.items():
            if follow_up["time"] <= current_time:
                pending_follow_ups.append({"phone": phone, "message": follow_up["message"]})
                del follow_ups[phone]  # Remove the follow-up after it's triggered

        return jsonify({"status": "success", "pending_follow_ups": pending_follow_ups})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)