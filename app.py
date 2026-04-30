from flask import Flask, jsonif, requests
import requests

app = Flask(__name__)


# الصفحة الرئيسية
@app.route("/")
def home():
    return jsonify({"status": "البوت يعمل"})

# استقبال إشارات TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

//@version=5
strategy("SMC + ICT + CRT PRO", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// =======================
// EMA + RSI
// =======================
ema = ta.ema(close, 50)
rsi = ta.rsi(close, 14)

// =======================
// الاتجاه
// =======================
bullish = close > ema
bearish = close < ema

// =======================
// السيولة (Liquidity Sweep)
// =======================
high_prev = ta.highest(high, 10)[1]
low_prev = ta.lowest(low, 10)[1]

sweep_buy = low < low_prev and close > low_prev
sweep_sell = high > high_prev and close < high_prev

// =======================
// BOS + CHoCH
// =======================
bos_up = close > high[2]
bos_down = close < low[2]

// =======================
// FVG (Fair Value Gap)
// =======================
fvg_up = low[1] > high[2]
fvg_down = high[1] < low[2]

// =======================
// Order Block بسيط
// =======================
bull_ob = close[2] < open[2] and close > high[2]
bear_ob = close[2] > open[2] and close < low[2]

// =======================
// CRT (كسر + رجوع)
// =======================
crt_buy = sweep_buy and close > low_prev
crt_sell = sweep_sell and close < high_prev

// =======================
// إشارات الدخول
// =======================
buy =
    bullish and
    sweep_buy and
    bos_up and
    fvg_up and
    bull_ob and
    rsi > 50

sell =
    bearish and
    sweep_sell and
    bos_down and
    fvg_down and
    bear_ob and
    rsi < 50

// =======================
// تنفيذ الصفقات
// =======================
if buy
    strategy.entry("BUY", strategy.long)

if sell
    strategy.entry("SELL", strategy.short)

// =======================
// رسم الإشارات
// =======================
plotshape(buy, title="BUY", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")
plotshape(sell, title="SELL", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")

// =======================
// معلومات
// =======================
plot(ema, color=color.orange, title="EMA 50")

// =======================
// تنبيهات (Webhook للبوت)
// =======================
reason_buy = "SMC + ICT + CRT + FVG + OB"
reason_sell = "SMC + ICT + CRT + FVG + OB"

if buy
    alert('{"signal":"BUY","price":"' + str.tostring(close) + '","reason":"' + reason_buy + '"}', alert.freq_once_per_bar_close)

if sell
    alert('{"signal":"SELL","price":"' + str.tostring(close) + '","reason":"' + reason_sell + '"}', alert.freq_once_per_bar_close)
 if not data:
        return jsonify({"error": "لا توجد بيانات"}), 400

    signal = data.get("signal")
    price = data.get("price")
    reason = data.get("reason")

    print("إشارة جديدة:")
    print("النوع:", signal)
    print("السعر:", price)
    print("السبب:", reason)

    return jsonify({
        "status": "تم الاستلام",
        "signal": signal,
        "price": price
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
