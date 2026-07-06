import yfinance as yf
import urllib.request
import json
import os
from datetime import datetime, timezone, timedelta

# LINE 設定改為從 GitHub Secrets 讀取，更安全
TOKEN = os.environ.get('LINE_TOKEN')
USER_ID = "U601a272f959493a2714777ec87256977"

def get_stock_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        info = ticker.info
        # 獲取過去 30 天數據計算 20 日布林通道
        hist = ticker.history(period="30d") 
        
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        eps = info.get('trailingEps')
        pe = info.get('trailingPE')
        
        # 計算布林通道 (MA20 + 2倍標準差)
        ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        std20 = hist['Close'].rolling(window=20).std().iloc[-1]
        upper = ma20 + (2 * std20)
        lower = ma20 - (2 * std20)
        
        return {
            "price": f"{price:.2f}" if price else "N/A",
            "eps": f"{eps:.2f}" if eps else "N/A",
            "pe": f"{pe:.2f}" if pe else "N/A",
            "upper": f"{upper:.2f}",
            "lower": f"{lower:.2f}"
        }
    except Exception as e:
        print(f"DEBUG: 抓取 {stock_id} 失敗: {e}")
        return None

def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*20]
    
    stocks = {'0050': '0050', '2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    
    for sid, sname in stocks.items():
        data = get_stock_data(sid)
        if data:
            report.append(f"【{sname}】")
            report.append(f"💰價:{data['price']} | EPS:{data['eps']} | PE:{data['pe']}")
            report.append(f"通道:{data['lower']}~{data['upper']}")
            report.append("-" * 15)
    
    report_text = "\n".join(report)
    
    # 發送至 LINE
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": report_text}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), 
                                 headers=headers)
    with urllib.request.urlopen(req) as response:
        print("✅ 推送成功")

if __name__ == "__main__":
    main()
