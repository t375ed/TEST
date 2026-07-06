import yfinance as yf
import urllib.request
import json
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get('LINE_TOKEN')
USER_ID = "U601a272f959493a2714777ec87256977"

def get_stable_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d") # 抓久一點確保技術指標穩定
        
        # 1. 股價
        price = hist['Close'].iloc[-1]
        
        # 2. 技術指標 (改用 pandas 計算，不依賴 info)
        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        
        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = (ema12 - ema26).iloc[-1]
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        return {
            "p": f"{price:.2f}",
            "bb": f"{ma20-2*std20:.1f}~{ma20+2*std20:.1f}",
            "macd": f"{macd:.2f}",
            "rsi": f"{rsi:.1f}"
        }
    except Exception as e:
        return None

def main():
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    report = ["📊 台股技術面報告"]
    
    for sid, sname in stocks.items():
        d = get_stable_data(sid)
        if d:
            report.append(f"\n【{sname}】\n💰價:{d['p']}\n布林:{d['bb']}\nMACD:{d['macd']} | RSI:{d['rsi']}")
    
    # 發送
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": "\n".join(report)}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    main()
