from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAfTlov6XyIBQeeZBY4JgdpfsGUfGmAYsKOBc6YFevS6Xdf09GSwsIrhvuWka0zxXtrn9eyTIxjfDowwzNhLHAchYOKhI2V2ZBhzZARSAWjDXaPmVgXxVxh73uScP5MgjePBTONV4ZBPHNTSO2Ve6ZBANl5WSOjErj3JZAt1kJIZAMxqaZC0PFGmQrFWzakqjg5oTfPRfBvOrgZDZD"
VERIFY_TOKEN = "routinemate_verify_123"


@app.route('/', methods=['GET'])
def home():
    return "RoutineMate Bot is running 🤖💙"


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]

                if "message" in messaging_event:
                    text = messaging_event["message"].get("text")

                    if text:
                        send_message(sender_id, f"👋 Hi! RoutineMate here. You said: {text}")

    return "ok", 200


def send_message(psid, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": psid},
        "message": {"text": message_text}
    }

    requests.post(url, json=payload)


if __name__ == '__main__':
    app.run()
