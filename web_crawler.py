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
        # 獲取基本資訊
        info = ticker.info
        hist = ticker.history(period="60d")
        
        # 抓取資料，若為空值則設為 0
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        eps = info.get('trailingEps', 0)
        pe = info.get('trailingPE', 0)
        
        # 財報數據 (若無數據，Yahoo 會回傳 None)
        gm = (info.get('grossMargins') or 0) * 100
        om = (info.get('operatingMargins') or 0) * 100
        nm = (info.get('profitMargins') or 0) * 100
        
        # 技術指標計算
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
            "p": f"{price:.2f}", "eps": f"{eps:.2f}", "pe": f"{pe:.2f}",
            "gm": f"{gm:.1f}%", "om": f"{om:.1f}%", "nm": f"{nm:.1f}%",
            "bb": f"{ma20-2*std20:.1f}~{ma20+2*std20:.1f}",
            "macd": f"{macd:.2f}", "rsi": f"{rsi:.1f}"
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    report = ["📊 完整財務技術分析報告"]
    
    for sid, sname in stocks.items():
        d = get_full_data(sid)
        if "error" in d:
            report.append(f"\n【{sname}】\n⚠️ 資料獲取異常")
        else:
            report.append(f"\n【{sname}】\n💰價:{d['p']} | EPS:{d['eps']} | PE:{d['pe']}\n"
                          f"毛:{d['gm']} 營:{d['om']} 稅後:{d['nm']}\n"
                          f"布林:{d['bb']}\nMACD:{d['macd']} | RSI:{d['rsi']}")
    
    # 發送
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": "\n".join(report)}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req) as res:
        print("✅ 執行結果:", res.status)

if __name__ == "__main__":
    main()
