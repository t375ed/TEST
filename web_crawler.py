import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.request
import json

# 設定區 (保持 Token 不變)
TOKEN = "S9r44KFKxG8T+fcql+KHLGZ0fy2/zHEMsNgWY91thDIDQDjKYFhzVp215VjeX8uivL4CqYvYr2lhc8if7nj8jsIqDQTR8fHKel2ulRPxbJUO2iw6+O5NAYFLTiRKLgfh7AWrrV/bPiAWpDSDJ5AHZQdB04t89/1O/w1cDnyilFU="
USER_ID = "U601a272f959493a2714777ec87256977"

def get_stock_data(stock_id):
    """
    抓取股價、財報與技術指標，並按區塊排版
    """
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d")
        info = ticker.info
        
        # 1. 抓取基礎數據
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 0)
        g_m = info.get('grossMargins', 0)
        o_m = info.get('operatingMargins', 0)
        n_m = info.get('profitMargins', 0)
        
        # 2. 計算技術指標
        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = ema12 - ema26
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 3. 排版
        return (f"💰現價:{price}\n"
                f"【獲利】毛利:{g_m*100:.1f}%|營益:{o_m*100:.1f}%|稅後:{n_m*100:.1f}%\n"
                f"【技術】布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}|MACD:{macd:.2f}|RSI:{rsi:.1f}\n"
                f"【估值】EPS:{eps}|P/E:{pe}|P/B:{pb}|ROE:{roe*100:.1f}%")
                
    except Exception as e:
        return f"資料抓取異常: {e}"

def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*15]
    
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    
    for sid, sname in stocks.items():
        data = get_stock_data(sid)
        report.append(f"【{sname}】\n{data}\n")
    
    report_text = "\n".join(report)
    
    # 發送至 LINE (使用偽裝瀏覽器請求)
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": report_text}]}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), 
                                 headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"✅ 成功！LINE 回應代碼: {response.status}")
    except Exception as e:
        print(f"❌ 發送失敗: {e}")

if __name__ == "__main__":
    main()
