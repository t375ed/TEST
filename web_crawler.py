import yfinance as yf          # 專門用來抓取 Yahoo Finance 的數據
import pandas as pd            # 資料運算工具，用來計算均線、布林通道等
from datetime import datetime, timezone, timedelta # 處理台灣時區的時間
import urllib.request          # 用來發送網路請求給 LINE 伺服器
import json                    # 用來將資料格式化成 JSON (LINE API 需要的格式)
import os                      # 用來讀取 GitHub 的環境變數

# 從 GitHub 設定的 Secrets 中讀取，這樣即使代碼公開，TOKEN 也不會外洩
TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

def get_stock_data(stock_id):
    """
    這是一個處理單支股票的函數，它會回傳組裝好的報表文字。
    """
    try:
        # 將輸入的代號（如 2330）加上 .TW，變成 Yahoo 財經認得的代號
        ticker = yf.Ticker(f"{stock_id}.TW")
        # 抓取 120 天數據，ffill() 是關鍵：把沒交易日期的空值用前一天填滿，解決 NaN 問題
        hist = ticker.history(period="120d").ffill()
        info = ticker.info
        
        # 抓取財報數據，如果該指標在 Yahoo 沒有提供，則回傳 N/A 或 0
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 0) or 0
        g_m = info.get('grossMargins', 0) or 0
        o_m = info.get('operatingMargins', 0) or 0
        n_m = info.get('profitMargins', 0) or 0
        
        # --- 技術指標計算 ---
        close = hist['Close'] # 取得最近的收盤價
        
        # 布林通道運算
        ma20 = close.rolling(20).mean().iloc[-1]   # 計算 20 日移動平均線 (中軌)
        std20 = close.rolling(20).std().iloc[-1]   # 計算 20 日標準差
        b_mid = float(ma20)                        # 布林中軌
        b_top = float(ma20 + (2 * std20))          # 布林上軌 (均線 + 2倍標準差)
        b_bot = float(ma20 - (2 * std20))          # 布林下軌 (均線 - 2倍標準差)
        
        # MACD 運算 (12日 EMA - 26日 EMA)
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = float(ema12 - ema26)
        
        # RSI 運算 (相對強弱指標)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(window=14).mean().iloc[-1] # 計算上漲平均
        loss = -delta.clip(upper=0).rolling(window=14).mean().iloc[-1] # 計算下跌平均
        # 避免除以零，若 loss 為 0 代表完全沒跌，RSI 強制設定為 100
        rsi = float(100 - (100 / (1 + (gain / loss)))) if loss != 0 else 100
        
        # 將計算出的指標用字串排版回傳，以便發送給 LINE
        return (f"💰現價:{price}\n"
                f"【獲利】毛利:{g_m*100:.1f}%|營益:{o_m*100:.1f}%|稅後:{n_m*100:.1f}%\n"
                f"【技術】布林底:{b_bot:.0f}|頂:{b_top:.0f}|均:{b_mid:.0f}|MACD:{macd:.2f}|RSI:{rsi:.1f}\n"
                f"【估值】EPS:{eps}|P/E:{pe}|P/B:{pb}|ROE:{roe*100:.1f}%")
                
    except Exception as e:
        # 如果爬蟲抓不到資料，回傳錯誤訊息，確保程式不會因為一支股票抓不到就整個崩潰
        return f"資料抓取異常: {e}"

def main():
    # 設定時區為 GMT+8 (台灣時間)
    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*15]
    
    # 這裡放你想追蹤的股票清單
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨','0050':'元大50'}
    
    # 迴圈：依序幫清單裡的每一支股票製作報告
    for sid, sname in stocks.items():
        data = get_stock_data(sid)
        report.append(f"【{sname}】\n{data}\n")
    
    # 將所有報告合併為一則訊息
    report_text = "\n".join(report)
    
    # 準備發送給 LINE API 的資料包 (包含你的使用者ID與訊息內容)
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": report_text}]}
    
    # 設定連線 Header，偽裝成 Chrome 瀏覽器請求，避免被 LINE 擋下
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 發送請求到 LINE API 伺服器
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), 
                                 headers=headers)
    
    # 嘗試連線並輸出結果到 GitHub Actions 日誌，讓你知道有沒有發送成功
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"✅ 成功！LINE 回應代碼: {response.status}")
    except Exception as e:
        print(f"❌ 發送失敗: {e}")

if __name__ == "__main__":
    main() # 程式的主入口，從這裡開始執行
