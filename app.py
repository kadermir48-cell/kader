from flask import Flask, request
import requests

app = Flask(name)

TOKEN = "PUT_YOUR_BOT_TOKEN"
CHAT_ID = "PUT_YOUR_CHAT_ID"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={data}")
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

if name == "main":
    app.run()
