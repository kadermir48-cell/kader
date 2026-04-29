import ccxt
import pandas as pd
import datetime

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"
# الاتصال بمنصة Binance
exchange = ccxt.binance()

# إعدادات السوق
symbol = "EUR/USD"
timeframe = "5m"

# لتجنب تكرار نفس الإشارة
last_signal = None

# =========================
# 🕒 فلتر وقت التداول (جلسات قوية)
# =========================
def وقت_التداول():
    hour = datetime.datetime.utcnow().hour
    return 7 <= hour <= 20  # من 7 إلى 20 (لندن + نيويورك)

# =========================
# 📊 دالة التحليل
# =========================
def تحليل():

    global last_signal

    try:

        # ❌ لا تتداول خارج الأوقات القوية
        if not وقت_التداول():
            return None

        # 📥 جلب البيانات
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)

        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

        # آخر شمعتين
        الحالية = df.iloc[-1]
        السابقة = df.iloc[-2]

        # =====================
        # 📈 المتوسط المتحرك EMA
        # =====================
        df["ema"] = df["close"].ewm(span=50).mean()
        ema = df["ema"].iloc[-1]

        # =====================
        # 📊 مؤشر RSI
        # =====================
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        rsi = df["rsi"].iloc[-1]

        # =====================
        # 💧 اصطياد السيولة (Liquidity Sweep)
        # =====================
        اعلى_سابق = df["high"].rolling(10).max().iloc[-2]
        ادنى_سابق = df["low"].rolling(10).min().iloc[-2]

        sweep_sell = الحالية["high"] > اعلى_سابق and الحالية["close"] < اعلى_سابق
        sweep_buy = الحالية["low"] > ادنى_سابق and الحالية["close"] <ادنى_سابق
       
        if __name__ == "__main__":
    threading.Thread(target=تشغيل).start()
    app.run(host="0.0.0.0", port=10000)
