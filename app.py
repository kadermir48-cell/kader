import ccxt
import pandas as pd
import ta
import time
import requests

# ========= إعدادات =========
TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

symbol = "EUR/USD"
timeframe = "5m"

exchange = ccxt.binance()

# ========= إرسال =========
def ارسال(نص):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": نص})

# ========= بيانات =========
def جلب():
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=150)
    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])
    df = df.astype(float)
    return df

# ========= كشف شمعة قوية =========
def شمعة_قوية(اخر, قبل):
    return (اخر["close"] > قبل["open"] and اخر["open"] < قبل["close"])

def شمعة_هابطة(اخر, قبل):
    return (اخر["close"] < قبل["open"] and اخر["open"] > قبل["close"])

# ========= تحليل احترافي =========
def تحليل():
    df = جلب()

    # مؤشرات
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    اخر = df.iloc[-1]
    قبل = df.iloc[-2]
    قبل2 = df.iloc[-3]

    # ===== BUY =====
    if (
        اخر["ema50"] > اخر["ema200"] and      # ترند
        قبل["low"] < قبل2["low"] and          # Sweep
        اخر["close"] > قبل["high"] and        # كسر للأعلى
        شمعة_قوية(اخر, قبل) and              # تأكيد
        اخر["rsi"] < 45
    ):
        return f"""📈 اشارة شراء احترافية

💱 {symbol}
⏱️ فريم: 5 دقائق

📊 Trend: صاعد
💧 Liquidity Sweep: تم
🔥 تأكيد شمعة: نعم
📉 RSI: {round(اخر["rsi"],2)}

⏳ مدة الصفقة: 5 دقائق
"""

    # ===== SELL =====
    elif (
        اخر["ema50"] < اخر["ema200"] and
        قبل["high"] > قبل2["high"] and
        اخر["close"] < قبل["low"] and
        شمعة_هابطة(اخر, قبل) and
        اخر["rsi"] > 55
    ):
        return f"""📉 اشارة بيع احترافية

💱 {symbol}
⏱️ فريم: 5 دقائق

📊 Trend: هابط
💧 Liquidity Sweep: تم
🔥 تأكيد شمعة: نعم
📈 RSI: {round(اخر["rsi"],2)}

⏳ مدة الصفقة: 5 دقائق
"""

    return None

last_signal = None

def تشغيل():
    global last_signal

    while True:
        try:
            اشارة = تحليل()

            if اشارة and اشارة != last_signal:
                ارسل(اشارة)
                last_signal = اشارة

            time.sleep(300)

        except Exception as e:
            print("خطأ:", e)
            time.sleep(3600)
import threading

if __name__ == "__mai__n":
    threading.Thread(target=تشغيل).start()
    app.run(host="0.0.0.0", port=10000)
