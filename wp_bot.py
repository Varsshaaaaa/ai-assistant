import requests

# Your Ultramsg instance details
WHATSAPP_API_URL = "https://api.ultramsg.com/instance108525/messages/chat"
WHATSAPP_TOKEN = ""

def send_whatsapp_message(phone_number, message):
    """
    Send a WhatsApp message using UltraMsg API.
    """
    data = {
        "token": WHATSAPP_TOKEN,
        "to": phone_number,
        "body": message
    }

    response = requests.post(WHATSAPP_API_URL, data=data)

    if response.status_code == 200:
        print("✅ WhatsApp message sent successfully!")
        return response.json()
    else:
        print("❌ Failed to send WhatsApp message.")
        return response.json()
    

from twilio.rest import Client

# Twilio credentials
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_WHATSAPP_NUMBER = ''  # e.g., 'whatsapp:+14155238886'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def fetch_whatsapp_messages():
    """Fetches messages from a WhatsApp chat using Twilio API."""
    messages = []
    
    # Fetch messages from the Twilio API
    try:
        # Fetch the last 10 messages sent to your Twilio WhatsApp number
        message_list = client.messages.list(to=TWILIO_WHATSAPP_NUMBER, limit=10)
        
        for message in message_list:
            messages.append({
                "from": message.from_,
                "text": message.body
            })
    except Exception as e:
        print(f"Error fetching WhatsApp messages: {str(e)}")
    
    return messages

# Test the function
if __name__ == "__main__":
    send_whatsapp_message("6369316373", "Hello! This is a test message from the AI Assistant.")
