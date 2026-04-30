from flask import Flask, jsonify
import pandas as pd
import requests
import ccxt
import datetime
import threading
import time

app = Flask(__name__)

# ===== الإعدادات =====
exchange = ccxt.binance()
symbol = "EUR/USD"
timeframe = "5m"

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

last_signal = None


# ===== وقت التداول =====
def trading_time():
    hour = datetime.datetime.utcnow().hour
    return 7 <= hour <= 20


# ===== تحليل CRT احترافي =====
def crt_analysis():
    global last_signal

    try:
        if not trading_time():
            return None

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

        current = df.iloc[-1]

        # ===== EMA =====
        df["ema"] = df["close"].ewm(span=50).mean()
        ema = df["ema"].iloc[-1]

        # ===== RSI =====
        delta = df["close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        rsi = df["rsi"].iloc[-1]

        # ===== Liquidity =====
        high_prev = df["high"].rolling(10).max().iloc[-2]
        low_prev = df["low"].rolling(10).min().iloc[-2]

        sweep_buy = current["low"] < low_prev and current["close"] > low_prev
        sweep_sell = current["high"] > high_prev and current["close"] < high_prev

        # ===== الاتجاه =====
        trend = "صاعد" if current["close"] > ema else "هابط"

        # ===== تقييم القوة =====
        strength = 0

        if sweep_buy or sweep_sell:
            strength += 40
        if current["close"] > ema:
            strength += 30
        if rsi > 50:
            strength += 30

        # ===== تحليل منطقي =====
        reason = ""
        signal = None

        # ===== BUY =====
        if sweep_buy and current["close"] > ema and rsi > 50:
            reason = """
- تم كسر قاع سابق (سحب سيولة)
- رجع السعر فوق المستوى
- الاتجاه صاعد (فوق EMA)
- RSI يدعم الصعود
"""
            signal = "BUY"

        # ===== SELL =====
        elif sweep_sell and current["close"] < ema and rsi < 50:
            reason = """
- تم كسر قمة (سحب سيولة)
- رجع السعر تحتها
- الاتجاه هابط
- RSI يدعم الهبوط
"""
            signal = "SELL"

        if signal is None:
            return None

        message = f"""
الزوج: {symbol}
الفريم: {timeframe}

نوع الصفقة: {signal}
السعر الحالي: {round(current['close'],2)}

RSI: {round(rsi,2)}
الاتجاه: {trend}
قوة الإشارة: {strength}%

التحليل:
{reason}

تعلم:
لا تدخل إلا إذا توفر:
1. سحب سيولة واضح
2. رجوع سريع
3. اتجاه واضح
4. تأكيد RSI
"""

        # منع التكرار
        if message == last_signal:
            return None

        last_signal = message
        return message

    except Exception as e:
        return f"Error: {str(e)}"


# ===== إرسال Telegram =====
def send_telegram(message):
    if TOKEN == "" or CHAT_ID == "":
        return

    url = f"https://api.telegram.org/bot{8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI}/sendMessage"
    requests.post(url, data={
        "chat_id": 6417116422,
        "text": message
    })


# ===== تشغيل تلقائي =====
def bot_loop():
    while True:
        signal = crt_analysis()

        if signal:
            print(signal)
            send_telegram(signal)

        time.sleep(60)


# ===== API =====
@app.route("/")
def home():
    return "CRT BOT WORKING"

@app.route("/signal")
def signal():
    result = crt_analysis()
    if result:
        return jsonify({"signal": result})
    return jsonify({"message": "no trade"})


# ===== تشغيل =====
if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    app.run(host="0.0.0.0", port=10000)
