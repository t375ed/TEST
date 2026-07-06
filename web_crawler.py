import yfinance as yf
import urllib.request
import json
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get('LINE_TOKEN')
USER_ID = "U601a272f959493a2714777ec87256977"

def get_full_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        info = ticker.info
        # 抓取較長歷史數據以計算 MACD/RSI
        hist = ticker.history(period="100d")
        
        # 財務數據
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        eps = info.get('trailingEps', 0)
        pe = info.get('trailingPE', 0)
        gross_margin = info.get('grossMargins', 0) * 100
        op_margin = info.get('operatingMargins', 0) * 100
        net_margin = info.get('profitMargins', 0) * 100
        
        # 技術指標計算
        close = hist['Close']
        # 布林通道
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        # MACD (12, 26, 9)
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = (ema12 - ema26).iloc[-1]
        # RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        return {
            "p": f"{price:.2f}", "eps": f"{eps:.2f}", "pe": f"{pe:.2f}",
            "gm": f"{gross_margin:.1f}%", "om": f"{op_margin:.1f}%", "nm": f"{net_margin:.1f}%",
            "bb": f"{ma20-2*std20:.1f}~{ma20+2*std20:.1f}",
            "macd": f"{macd:.2f}", "rsi": f"{rsi:.1f}"
        }
    except Exception as e:
        print(f"DEBUG: {stock_id} 錯誤: {e}")
        return None

def main():
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    report = [f"📊 進階財務技術報告"]
    
    for sid, sname in stocks.items():
        d = get_full_data(sid)
        if d:
            report.append(f"\n【{sname}】\n💰{d['p']} | EPS:{d['eps']} | PE:{d['pe']}\n"
                          f"毛:{d['gm']} 營:{d['om']} 稅後:{d['nm']}\n"
                          f"布林:{d['bb']}\nMACD:{d['macd']} | RSI:{d['rsi']}")
    
    # 發送訊息
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": "\n".join(report)}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    main()
