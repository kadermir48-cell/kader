import ccxt
import pandas as pd
import datetime

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

exchange = ccxt.binance()

symbol = "BTC/USDT"
timeframe = "5m"

last_signal = None

# =========================
# فلتر الجلسات (أفضل وقت تداول)
# =========================
def وقت_التداول():
    hour = datetime.datetime.utcnow().hour
    return 7 <= hour <= 20

# =========================
# تحليل السوق
# =========================
def تحليل():

    global last_signal

    try:
        if not وقت_التداول():
            return None

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

        current = df.iloc[-1]
        prev = df.iloc[-2]

        # =====================
        # EMA (الاتجاه)
        # =====================
        df["ema"] = df["close"].ewm(span=50).mean()
        ema = df["ema"].iloc[-1]

        # =====================
        # RSI (الزخم)
        # =====================
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        rsi = df["rsi"].iloc[-1]

        # =====================
        # Liquidity Sweep
        # =====================
        high_prev = df["high"].rolling(10).max().iloc[-2]
        low_prev = df["low"].rolling(10).min().iloc[-2]

        sweep_sell = current["high"] > high_prev and current["close"] < high_prev
        sweep_buy = current["low"] < low_prev and current["close"] > low_prev

        # =====================
        # تأكيد شمعة قوية
        # =====================
        bullish = current["close"] > current["open"]
        bearish = current["close"] < current["open"]

        signal = None

        # =====================
        # BUY
        # =====================
        if (
            sweep_buy and
            current["close"] > ema and
            rsi > 50 and
            bullish
        ):
            signal = f"""
🟢 BUY (Smart Money)

📊 السبب:
- كسر سيولة تحت
- الاتجاه صاعد
- RSI قوي
- شمعة صاعدة

💰 السعر: {current['close']}
📈 RSI: {round(rsi,2)}
"""

        # =====================
        # SELL
        # =====================
        elif (
            sweep_sell and
            current["close"] < ema and
            rsi < 50 and
            bearish
        ):
            signal = f"""
🔴 SELL (Smart Money)

📊 السبب:
- كسر سيولة فوق
- الاتجاه هابط
- RSI ضعيف
- شمعة هابطة

💰 السعر: {current['close']}
📉 RSI: {round(rsi,2)}
"""

        # منع التكرار
        if signal == last_signal:
            return None

        last_signal = signal
        return signal

    except Exception as e:
        print("خطأ:", e)
        return None

