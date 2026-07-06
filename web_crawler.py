import yfinance as yf
import urllib.request
import json
import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get('LINE_TOKEN')
USER_ID = "U601a272f959493a2714777ec87256977"

# 抓取證交所官方每日基本面資料 (本益比、殖利率、股價淨值比)
def get_twse_fundamentals():
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_d"
        res = requests.get(url)
        data = res.json()
        fund_dict = {}
        for item in data:
            fund_dict[item['Code']] = {
                'pe': item['PEratio'],
                'pb': item['PBratio'],
                'yield': item['DividendYield']
            }
        return fund_dict
    except Exception:
        return {}

twse_data = get_twse_fundamentals()

def get_full_data(stock_id):
    try:
        # 抓取技術面歷史股價
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d") 
        
        if hist.empty:
            return "❌ 抓取失敗：無歷史資料"

        close = hist['Close']
        price = close.iloc[-1]
        
        # --- 基本面計算 ---
        pe = twse_data.get(stock_id, {}).get('pe', 'N/A')
        pb = twse_data.get(stock_id, {}).get('pb', 'N/A')
        dy = twse_data.get(stock_id, {}).get('yield', 'N/A')
        
        # 透過 股價/本益比 反推 EPS
        try:
            if pe != 'N/A' and float(pe) > 0:
                eps = f"{price / float(pe):.2f}"
            else:
                eps = "N/A"
        except:
            eps = "N/A"

        # --- 技術面計算 ---
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = (ema12 - ema26).iloc[-1]
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # 組合報告
        report = (f"💰價:{price:.0f} | EPS:{eps} | PE:{pe}\n"
                  f"淨值比:{pb} | 殖利率:{dy}%\n"
                  f"布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}\n"
                  f"MACD:{macd:.2f} | RSI:{rsi:.1f}")
        return report
        
    except Exception as e:
        return f"⚠️ 錯誤: {str(e)}"

def main():
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    report = ["📊 完整基本面與波段報告"]
    
    for sid, sname in stocks.items():
        d = get_full_data(sid)
        report.append(f"\n【{sname}】\n{d}")
    
    # 發送 LINE 訊息
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": "\n".join(report)}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    main()
