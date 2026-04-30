from flask import Flask, jsonify
import requests
import pandas as pd

app = Flask(name)

def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
    data = requests.get(url).json()

# =========================
# جلب البيانات
# =========================
def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=150"
    data = requests.get(url, timeout=10).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df

# =========================
# RSI
# =========================
def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# =========================
# التحليل
# =========================
def analyze():
    df = get_data()

    df["ema"] = df["close"].ewm(span=50).mean()
    df["rsi"] = calculate_rsi(df)

    current = df.iloc[-1]

    # Liquidity
    high_prev = df["high"].rolling(10).max().iloc[-2]
    low_prev = df["low"].rolling(10).min().iloc[-2]

    sweep_buy = current["low"] < low_prev and current["close"] > low_prev
    sweep_sell = current["high"] > high_prev and current["close"] < high_prev

    # BOS
    bos_up = current["close"] > df["high"].iloc[-3]
    bos_down = current["close"] < df["low"].iloc[-3]

    # FVG
    fvg_up = df["low"].iloc[-2] > df["high"].iloc[-3]
    fvg_down = df["high"].iloc[-2] < df["low"].iloc[-3]

    # Order Block بسيط
    ob_buy = df["low"].iloc[-4]
    ob_sell = df["high"].iloc[-4]

    near_ob_buy = current["close"] <= ob_buy * 1.01
    near_ob_sell = current["close"] >= ob_sell * 0.99

    # Trend
    trend = "صاعد" if current["close"] > current["ema"] else "هابط"

    reasons = []
    score = 0

    # =========================
    # تحليل الشروط
    # =========================

    if trend == "صاعد":
        reasons.append("الاتجاه صاعد")
        score += 1
    else:
        reasons.append("الاتجاه هابط")
        score += 1

    if current["rsi"] > 50:
        reasons.append("RSI فوق 50")
        score += 1
    else:
        reasons.append("RSI تحت 50")
        score += 1

    if sweep_buy:
        reasons.append("سحب سيولة شراء")
        score += 1

    if sweep_sell:
        reasons.append("سحب سيولة بيع")
        score += 1

    if bos_up:
        reasons.append("كسر هيكل صاعد")
        score += 1

    if bos_down:
        reasons.append("كسر هيكل هابط")
        score += 1

    if fvg_up:
        reasons.append("وجود فجوة سعرية صاعدة")
        score += 1

    if fvg_down:
        reasons.append("وجود فجوة سعرية هابطة")
        score += 1

    if near_ob_buy:
        reasons.append("السعر قريب من منطقة طلب")
        score += 1

    if near_ob_sell:
        reasons.append("السعر قريب من منطقة عرض")
        score += 1

    # =========================
    # الإشارة
    # =========================
    signal = "لا يوجد"

    if sweep_buy and bos_up and fvg_up and trend == "صاعد" and current["rsi"] > 50:
        signal = "شراء"

    elif sweep_sell and bos_down and fvg_down and trend == "هابط" and current["rsi"] < 50:
        signal = "بيع"

    return {
        "السعر": float(current["close"]),
        "الاتجاه": trend,
        "RSI": float(current["rsi"]),
        "الإشارة": signal,
        "قوة_الصفقة": score,
        "الأسباب": reasons
    }

# =========================
# Routes
# =========================
@app.route("/")
def home():
    return jsonify({"الحالة": "يعمل"})

@app.route("/signal")
def signal():
    return jsonify(analyze())
   
