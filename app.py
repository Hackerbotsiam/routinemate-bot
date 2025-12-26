from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "RoutineMate Bot is running 🤖💙", 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def webhook_post():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):

                if event.get("message", {}).get("is_echo"):
                    continue

                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_text = event["message"]["text"]

                    reply = f"🤖 RoutineMate Bot\n\nতুমি লিখেছো:\n👉 {user_text}"
                    send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200


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
