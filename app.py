# -*- coding: utf-8 -*-
import datetime
import threading

TOKEN = "8738394543:AAGVtHjCJcNIzIxFjfBeAJEG1CgUMvVPbLI"
CHAT_ID = "6417116422"

exchange = ccxt.binance()
signal = f"""
PAIR: EUR/USD (5m)

BUY SIGNAL

Entry: {round(current['close'],2)}
RSI: {round(rsi,2)}

"""

"🟢" CALL UP
"⏱️" 5 Minute

"📍" Entry: 64250
"📈" RSI: 58
"📊" Trend: Bullish

"🔥" Strength: 82%

"📌" السبب:
- Liquidity Sweep
- Trend Up
- Strong Candle


"🤖" Smart Money Bot
score = 0

# اتجاه
if current["close"] > ema:
    score += 25

# RSI
if rsi > 55:
    score += 25

# سيولة
if sweep_buy or sweep_sell:
    score += 25

# شمعة قوية
if bullish or bearish:
    score += 25

strength = score
trend = "Bullish 📈" if current["close"] > ema else "Bearish 📉"
signal = f"""
📊 {symbol} ({timeframe})

"🟢" CALL UP
"⏱️" 5 Minute

"📍" Entry: {round(current['close'],2)}
"📈" RSI: {round(rsi,2)}
"📊" Trend: {trend}

"🔥" Strength: {strength}%

"📌" السبب:
- Liquidity Sweep
- Trend Confirmed
- RSI Strong
- Bullish Candle


"🤖" Smart Money Bot
signal = f"""
"📊" {symbol} ({timeframe})

"🔴" PUT DOWN
"⏱️" 5 Minute

"📍" Entry: {round(current['close'],2)}
"📉" RSI: {round(rsi,2)}
"📊" Trend: {trend}

"🔥" Strength: {strength}%

"📌" السبب:
- Liquidity Sweep
- Trend Confirmed
- RSI Weak
- Bearish Candle

"🤖" Smart Money Bot
if strength < 70:
    return None
global last_time

if current["time"] == last_time:
    return None

last_time = current["time"]
import time

def تشغيل():
    while True:
        signal = تحليل()
        if signal:
            ارسال_تيليجرام(signal)
        time.sleep(30)
        def رسم_الشارت(df, signal_type):

    df_plot = df.copy()
    df_plot['time'] = pd.to_datetime(df_plot['time'], unit='ms')
    df_plot.set_index('time', inplace=True)

    # تحديد لون الإشارة
    color = 'g' if signal_type == "buy" else 'r'

    apds = []

    # رسم EMA
    apds.append(mpf.make_addplot(df_plot['close'].ewm(span=50).mean(), color='blue'))

    # حفظ الصورة
    file_name = "chart.png"

    mpf.plot(
        df_plot,
        type='candle',
        style='charles',
        addplot=apds,
        volume=False,
        savefig=file_name
    )
    def ارسال_صورة(file_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(file_path, 'rb') as photo:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "caption": caption
        }, files={"photo": photo})
        def ارسال_صورة(file_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(file_path, 'rb') as photo:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "caption": caption
        }, files={"photo": photo})
  
