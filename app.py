from flask import Flask, jsonify
import pandas as pd
import requests

app = Flask(__name__)

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"
[30/04/2026 01:55] Ka Der: from flask import Flask, jsonify
import pandas as pd
import requests

def get_data():
    url = "https://apitrading view.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
    data = requests.get(url).json()

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

    trend = "bullish" if current["close"] > current["ema"] else "bearish"

    signal = "none"

    if sweep_buy and current["close"] > current["ema"] and current["rsi"] > 50:
        signal = "buy"
    elif sweep_sell and current["close"] < current["ema"] and current["rsi"] < 50:
        signal = "sell"

    return {
        "price": float(current["close"]),
        "ema": float(current["ema"]),
        "rsi": float(current["rsi"]),
        "trend": trend,
        "signal": signal
    }

@app.route("/")
def home():
    return jsonify({"status": "running"})

@app.route("/signal")
def signal():
    return jsonify(analyze())
[30/04/2026 02:09] Ka Der: from flask import Flask, jsonify
import pandas as pd
import requests

app = Flask(name)

TOKEN = "PUT_YOUR_TOKEN_HERE"
CHAT_ID = "PUT_YOUR_CHAT_ID_HERE"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=120"
    data = requests.get(url).json()

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

    trend = "bullish" if current["close"] > current["ema"] else "bearish"

    # FVG بسيط
    fvg_up = df["low"].iloc[-2] > df["high"].iloc[-3]
    fvg_down = df["high"].iloc[-2] < df["low"].iloc[-3]

    signal = "none"

    if sweep_buy and trend == "bullish" and current["rsi"] > 50 and fvg_up:
        signal = "buy"

    elif sweep_sell and trend == "bearish" and current["rsi"] < 50 and fvg_down:
        signal = "sell"

    return {
        "price": float(current["close"]),
        "ema": float(current["ema"]),
        "rsi": float(current["rsi"]),
        "trend": trend,
        "signal": signal
    }

@app.route("/")
def home():
    return jsonify({"status": "running"})

@app.route("/signal")
def signal():
    return jsonify(analyze())

@app.route("/run")
def run():
    result = analyze()

    if result["signal"] != "none":
        message = f"Signal: {result['signal']}\nPrice: {result['price']}\nTrend: {result['trend']}"
        send_telegram(message)

    return jsonify(result)
