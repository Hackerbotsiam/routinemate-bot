from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# 🔐 Tokens (Render Environment Variables)
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🤖 Configure Gemini safely
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")
else:
    gemini_model = None
    print("⚠️ GEMINI_API_KEY not found. AI replies disabled.")


# 🏠 Health check
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

                # Ignore bot echo
                if event.get("message", {}).get("is_echo"):
                    continue

                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_text = event["message"]["text"]

                    reply = handle_message(user_text)
                    send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200


# 🧠 Main brain
def handle_message(user_text):
    text = user_text.lower().strip()

    # ⚡ Fast replies
    if text in ["hi", "hello", "hey"]:
        return "👋 হাই! আমি RoutineMate 🤖\nতুমি যেকোনো প্রশ্ন করতে পারো।"

    if "routine" in text or "রুটিন" in text:
        return (
            "📅 Basic Daily Routine:\n"
            "🌅 সকাল 6–7 → Revision\n"
            "📘 10–1 → Study\n"
            "🌙 রাত 8–10 → Practice\n\n"
            "চাও তো আমি তোমার জন্য কাস্টম রুটিন বানিয়ে দেবো 🙂"
        )

    if "ডিপ্রেস" in text or "sad" in text or "ভালো নেই" in text:
        return "💙 তুমি একা না। ধীরে শ্বাস নাও, পানি খাও। আমি আছি 🙂"

    # 🤖 Gemini AI (ANY QUESTION)
    if gemini_model:
        try:
            prompt = f"""
তুমি RoutineMate নামে একজন সহানুভূতিশীল Bangla AI assistant।
তুমি মানুষের পড়াশোনা, রুটিন, মানসিক সাপোর্ট, লাইফ প্রশ্নে সাহায্য করো।
উত্তর সংক্ষিপ্ত, মানবিক ও বাংলায় দাও।

User: {user_text}
"""

            response = gemini_model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print("❌ GEMINI ERROR:", e)

    # 🛟 Fallback
    return "⚠️ দুঃখিত, এখন আমি উত্তর দিতে পারছি না। একটু পর আবার চেষ্টা করো।"


# 🚀 Send message to Messenger
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
