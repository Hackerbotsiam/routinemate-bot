from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 🔐 Environment Variables (Render-এ সেট করা থাকতে হবে)
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# 🏠 Health Check
@app.route("/", methods=["GET"])
def home():
    return "RoutineMate Bot is running 🤖💙", 200


# ✅ Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


# 📩 Receive Messages
@app.route("/webhook", methods=["POST"])
def webhook_post():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):

                # ❌ Bot-এর নিজের message ignore
                if event.get("message", {}).get("is_echo"):
                    continue

                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_text = event["message"]["text"].lower()

                    # 🧠 Smart Reply Logic
                    if "hi" in user_text or "hello" in user_text or "হাই" in user_text:
                        reply = (
                            "👋 হাই!\n"
                            "আমি RoutineMate 🤖\n"
                            "আমি তোমার পড়াশোনা ও দৈনন্দিন রুটিনে সাহায্য করি।"
                        )

                    elif "পড়ার সময়" in user_text or "study time" in user_text:
                        reply = (
                            "📚 পড়ার সেরা সময়:\n"
                            "🌅 সকাল ৬–৯ টা\n"
                            "🌙 রাত ৮–১১ টা\n\n"
                            "এই সময়গুলোতে মন সবচেয়ে ফোকাসড থাকে।"
                        )

                    elif "ডিপ্রেস" in user_text or "sad" in user_text or "tired" in user_text:
                        reply = (
                            "💙 আমি বুঝতে পারছি তুমি ভালো নেই।\n"
                            "একটু বিরতি নাও, পানি খাও, গভীর শ্বাস নাও।\n"
                            "তুমি পারবে—আমি আছি 🤗"
                        )

                    elif "routine বানাও" in user_text or "daily routine" in user_text or "রুটিন" in user_text:
                        reply = (
                            "📅 Daily Study Routine:\n\n"
                            "⏰ 6:00–7:00 AM → Revision\n"
                            "📘 10:00–1:00 PM → Core Study\n"
                            "🧠 4:00–6:00 PM → Practice\n"
                            "🌙 8:00–10:00 PM → Light Study\n\n"
                            "চাও তো আমি কাস্টম রুটিনও বানাতে পারি 🙂"
                        )

                    else:
                        reply = (
                            "🤖 আমি এখনো শেখার পর্যায়ে আছি।\n\n"
                            "👉 try করো:\n"
                            "• hi\n"
                            "• পড়ার সময় বলো\n"
                            "• routine বানাও\n"
                            "• আজ আমি ডিপ্রেসড"
                        )

                    send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200


# 🚀 Send Message Function
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
