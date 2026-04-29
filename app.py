from flask import Flask
import requests
import time
from datetime import datetime
import threading

app = Flask(__name__)

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "5m"

last_signal_time = {}

# ===== جلب البيانات =====
def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit=150"
    data = requests.get(url).json()

    closes = [float(c[4]) for c in data]
    opens = [float(c[1]) for c in data]
    highs = [float(c[2]) for c in data]
    lows = [float(c[3]) for c in data]

    return closes, opens, highs, lows

# ===== EMA =====
def ema(data, period):
    k = 2 / (period + 1)
    ema_val = data[0]
    for price in data:
        ema_val = price * k + ema_val * (1 - k)
    return ema_val

# ===== RSI =====
def rsi(data, period=14):
    gains, losses = [], []
    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ===== MACD =====
def macd(data):
    return ema(data, 12) - ema(data, 26)

# ===== تحليل نخبة =====
def analyze(symbol):
    closes, opens, highs, lows = get_data(symbol)

    price = closes[-1]
    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    ema50 = ema(closes, 50)

    rsi_val = rsi(closes)
    macd_val = macd(closes)

    last_open = opens[-1]
    last_close = closes[-1]

    body = abs(last_close - last_open)
    candle_size = highs[-1] - lows[-1]

    strong_candle = body > (candle_size * 0.5)

    hour = datetime.now().hour
    good_time = 9 <= hour <= 22

    now = time.time()
    if symbol in last_signal_time and now - last_signal_time[symbol] < 900:
        return None

    signal = None
    reason = ""
    confidence = ""

    # 🟢 BUY نخبة
    if (
        ema9 > ema21 > ema50 and
        rsi_val < 40 and
        macd_val > 0 and
        last_close > last_open and
        strong_candle and
        good_time
    ):
        signal = "🟢 شراء نخبة"
        reason = "اتجاه صاعد قوي + RSI منخفض + MACD إيجابي + شمعة قوية"
        confidence = "نخبة 🔥🔥🔥🔥"
        last_signal_time[symbol] = now

    # 🔴 SELL نخبة
    elif (
        ema9 < ema21 < ema50 and
        rsi_val > 60 and
        macd_val < 0 and
        last_close < last_open and
        strong_candle and
        good_time
    ):
        signal = "🔴 بيع نخبة"
        reason = "اتجاه هابط قوي + RSI مرتفع + MACD سلبي + شمعة قوية"
        confidence = "نخبة 🔥🔥🔥🔥"
        last_signal_time[symbol] = now

    if signal is None:
        return None

    return {
        "symbol": symbol,
        "signal": signal,
        "price": round(price, 2),
        "rsi": round(rsi_val, 2),
        "macd": round(macd_val, 4),
        "confidence": confidence,
        "reason": reason
    }

# ===== إرسال =====
def send_signal(result):
    time_now = datetime.now().strftime("%H:%M")

    message = (
        f"📊 إشارة نخبة (5 دقائق)\n\n"
        f"💱 الزوج: {result['symbol']}\n"
        f"📍 الصفقة: {result['signal']}\n\n"
        f"💰 السعر: {result['price']}\n"
        f"📊 RSI: {result['rsi']}\n"
        f"📉 MACD: {result['macd']}\n\n"
        f"🔥 القوة: {result['confidence']}\n\n"
        f"📖 السبب:\n{result['reason']}\n\n"
        f"📚 تعلم:\n"
        f"هذه الصفقة تحققت فيها كل شروط النخبة (Trend + Momentum + Candle)\n\n"
        f"⏰ الوقت: {time_now}"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message
    })
    # ===== تشغيل تلقائي =====
def run_bot():
    while True:
        try:
            for symbol in SYMBOLS:
                result = analyze(symbol)
                if result:
                    send_signal(result)
            time.sleep(300)
        except:
            time.sleep(60)

threading.Thread(target=run_bot).start()

# الصفحة الرئيسية
@app.route('/')
def home():
    return "ELITE BOT RUNNING 🚀"

# دالة ارسال رسالة
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# تشغيل البوت
def run_bot():
    while True:
        send_telegram_message("🚀 البوت يعمل الآن!")
        time.sleep(60)

# تشغيل البوت في الخلفية
threading.Thread(target=run_bot).start()

# تشغيل السيرفر

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
