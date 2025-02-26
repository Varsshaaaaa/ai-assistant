# Personal Ai Communication Assistant

## Introduction
This project is designed to simplify and enhance digital communication by integrating **Gmail, Slack, and WhatsApp**. The assistant helps manage emails, summarize messages, and generate AI-powered responses, reducing manual effort and improving efficiency.

## Key Features
- **📩 Email Management**: Fetches, categorizes, and summarizes emails automatically.
- **💬 WhatsApp Assistant**: Sends and receives messages, provides smart replies, and summarizes chats.
- **🏢 Slack Integration**: Retrieves messages and assists in team communication.
- **🤖 AI-Powered Responses**: Uses **Google Gemini AI** to generate smart replies.
- **🔄 Automated Task Scheduling**: Manages message retrieval and responses through **APScheduler**.

## Technologies Used
- **Programming Language**: Python
- **Framework**: Flask
- **AI Models**: Google Gemini AI, T5 (for text summarization)
- **APIs**: Gmail API, Slack API, Twilio WhatsApp API, UltraMsg API
- **Database**: SQLite (for storing authentication tokens)
- **Deployment**: Docker (optional)

## How to Set Up
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/ai-assistant.git
   cd ai-assistant
   ```
2. **Install Required Dependencies**:
   ```bash
   pip install flask google-auth google-auth-oauthlib google-auth-httplib2 googleapiclient requests transformers torch apscheduler python-dotenv
   ```
3. **Configure API Keys**:
   - Create a `.env` file and store your API keys securely.
   ```bash
   GEMINI_API_KEY=your_gemini_api_key
   SLACK_BOT_TOKEN=your_slack_token
   ```
4. **Authenticate Gmail Access**:
   - Ensure `credentials.json` is in the project directory.
   - Run:
   ```bash
   python gmail_auth.py
   ```
5. **Start the Application**:
   ```bash
   python app.py
   ```

## Security Best Practices
🚨 **Do Not Hardcode API Keys** – Always use environment variables.
🔒 **Secure Credentials** – Restrict access to `token.json` and `.env` files.

## Future Improvements
- 🌍 **Support for Multiple Languages** in AI replies.
- 🔑 **User Authentication** for improved security.
- 🚀 **Optimized Performance** through batch processing of API requests.


