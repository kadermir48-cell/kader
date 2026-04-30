from flask import Flask, jsonify
import pandas as pd
import requests

app = Flask(name)

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
    response = requests.get(url, timeout=10)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze():
    df = get_data()

    df["ema"] = df["close"].ewm(span=50).mean()
    df["rsi"] = calculate_rsi(df)

    current = df.iloc[-1]

    high_prev = df["high"].rolling(10).max().iloc[-2]
    low_prev = df["low"].rolling(10).min().iloc[-2]

    sweep_buy = current["low"] < low_prev and current["close"] > low_prev
    sweep_sell = current["high"] > high_prev and current["close"] < high_prev

    الاتجاه = "صاعد" if current["close"] > current["ema"] else "هابط"

    الاشارة = "لا يوجد"

    if sweep_buy and current["close"] > current["ema"] and current["rsi"] > 50:
        الاشارة = "شراء"

    elif sweep_sell and current["close"] < current["ema"] and current["rsi"] < 50:
        الاشارة = "بيع"

    return {
        "السعر": float(current["close"]),
        "المتوسط": float(current["ema"]),
        "RSI": float(current["rsi"]),
        "الاتجاه": الاتجاه,
        "الاشارة": الاشارة
    }

def send_telegram(message):
    if TOKEN == "" or CHAT_ID == "":
        return

    url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

@app.route("/")
def home():
    return jsonify({"الحالة": "يعمل"})

@app.route("/signal")
def signal():
    result = analyze()

    message = (
        "السعر: " + str(result["السعر"]) + "\n" +
        "الاتجاه: " + result["الاتجاه"] + "\n" +
        "الاشارة: " + result["الاشارة"] + "\n" +
        "RSI: " + str(result["RSI"])
    )

    send_telegram(message)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
