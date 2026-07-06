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
        # 關鍵修正：必須是全大寫的 .TW
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d") 
        
        if hist.empty:
            return "❌ 抓取失敗：Yahoo 無歷史資料"

        # 1. 股價
        price = hist['Close'].iloc[-1]
        
        # 2. 技術指標
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
        
        return f"💰價:{price:.2f}\n布林:{ma20-2*std20:.1f}~{ma20+2*std20:.1f}\nMACD:{macd:.2f} | RSI:{rsi:.1f}"
        
    except Exception as e:
        # 關鍵修正：將錯誤直接傳到 LINE，不要回傳 None
        return f"⚠️ 計算錯誤: {str(e)}"

def main():
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    report = ["📊 台股技術面報告 (除錯版)"]
    
    for sid, sname in stocks.items():
        d = get_stable_data(sid)
        # 直接印出結果，不管成功或失敗都會顯示
        report.append(f"\n【{sname}】\n{d}")
    
    # 發送
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": "\n".join(report)}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    main()
