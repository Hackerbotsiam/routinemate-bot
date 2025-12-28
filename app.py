from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# 🔐 Tokens
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🤖 Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET"])
def home():
    return "RoutineMate Bot is running 🤖💙", 200


# ✅ Webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


# 📩 Receive messages
@app.route("/webhook", methods=["POST"])
def webhook_post():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):

                # Ignore echo
                if event.get("message", {}).get("is_echo"):
                    continue

                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_text = event["message"]["text"]

                    reply = handle_message(user_text)
                    send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200


# 🧠 Message logic
def handle_message(user_text):
    text = user_text.lower()

    # Basic fast replies
    if "hi" in text or "hello" in text:
        return "👋 হাই! আমি RoutineMate 🤖\nতুমি যেকোনো প্রশ্ন করতে পারো।"

    if "routine" in text or "রুটিন" in text:
        return (
            "📅 Basic Daily Routine:\n"
            "🌅 সকাল 6–7 → Revision\n"
            "📘 10–1 → Study\n"
            "🌙 রাত 8–10 → Practice\n\n"
            "তুমি চাইলে আমি কাস্টম রুটিনও বানাতে পারি 🙂"
        )

    if "ডিপ্রেস" in text or "sad" in text:
        return "💙 তুমি একা না। ছোট বিরতি নাও, পানি খাও, আমি আছি 🙂"

    # 🤖 Gemini AI fallback (ANY QUESTION)
    try:
        prompt = f"""
তুমি একজন সহানুভূতিশীল Bangla AI assistant।
User এর প্রশ্নের সহজ, মানবিক উত্তর দাও।

User: {user_text}
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return "⚠️ দুঃখিত, এখন AI উত্তর দিতে পারছি না। একটু পর চেষ্টা করো।"


# 🚀 Send message
def send_message(psid, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    payload = {
        "recipient": {"id": psid},
        "message": {"text": text}
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}

    requests.post(url, params=params, json=payload)


if __name__ == "__main__":
    app.run()
