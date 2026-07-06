import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.request
import json
import os  # 用於讀取 GitHub Secrets 的環境變數

# 從系統環境變數中讀取，這樣程式碼內就不會出現你的隱私資訊
TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

def get_stock_data(stock_id):
    """
    功能：抓取股價、財報與技術指標，並按區塊排版
    """
    try:
        # 建立股票物件並抓取資料，使用 ffill() 填補斷層避免 NaN
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d").ffill()
        info = ticker.info
        
        # 基礎財報數據，若無資料則給予 0 或 N/A
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 0) or 0
        g_m = info.get('grossMargins', 0) or 0
        o_m = info.get('operatingMargins', 0) or 0
        n_m = info.get('profitMargins', 0) or 0
        
        # 技術指標計算 (布林通道、MACD、RSI)
        close = hist['Close']
        
        # 布林通道：均線、上軌、下軌
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        b_mid = float(ma20)
        b_top = float(ma20 + (2 * std20))
        b_bot = float(ma20 - (2 * std20))
        
        # MACD：快慢線差值
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = float(ema12 - ema26)
        
        # RSI：相對強弱指標
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(window=14).mean().iloc[-1]
        loss = -delta.clip(upper=0).rolling(window=14).mean().iloc[-1]
        rsi = float(100 - (100 / (1 + (gain / loss)))) if loss != 0 else 100
        
        # 排版輸出
        return (f"💰現價:{price}\n"
                f"【獲利】毛利:{g_m*100:.1f}%|營益:{o_m*100:.1f}%|稅後:{n_m*100:.1f}%\n"
                f"【技術】布林底:{b_bot:.0f}|頂:{b_top:.0f}|均:{b_mid:.0f}|MACD:{macd:.2f}|RSI:{rsi:.1f}\n"
                f"【估值】EPS:{eps}|P/E:{pe}|P/B:{pb}|ROE:{roe*100:.1f}%")
                
    except Exception as e:
        return f"資料抓取異常: {e}"

def main():
    # 檢查 TOKEN 是否正確載入
    if not TOKEN or not USER_ID:
        print("❌ 錯誤：找不到 TOKEN 或 USER_ID，請檢查 GitHub Secrets 設定")
        return

    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*15]
    
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    
    for sid, sname in stocks.items():
        data = get_stock_data(sid)
        report.append(f"【{sname}】\n{data}\n")
    
    report_text = "\n".join(report)
    
    # 偽裝瀏覽器請求發送至 LINE
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
