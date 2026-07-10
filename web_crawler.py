import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.request
import json
import os

TOKEN = os.environ.get("LINE_TOKEN")

def get_stock_data(stock_id, is_etf=False):
    """
    功能：抓取股價、財報與技術指標 (修正：強制從歷史資料取最新價)
    """
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        # 抓取近 120 天數據並補值
        hist = ticker.history(period="120d").ffill()
        if hist.empty:
            return "資料抓取異常: 查無股價資料"
            
        info = ticker.info
        
        # 【修正】直接從 hist 取最新收盤價，比 info.get('currentPrice') 更穩定
        price = hist['Close'].iloc[-1]
        
        # 計算技術指標
        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        b_mid = float(ma20)
        b_top = float(ma20 + (2 * std20))
        b_bot = float(ma20 - (2 * std20))
        
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = float(ema12 - ema26)
        
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(window=14).mean().iloc[-1]
        loss = -delta.clip(upper=0).rolling(window=14).mean().iloc[-1]
        rsi = float(100 - (100 / (1 + (gain / loss)))) if loss != 0 else 100
        
        # 組裝報告
        report = f"💰現價:{price:.2f}\n【技術】布林底:{b_bot:.0f}|頂:{b_top:.0f}|均:{b_mid:.0f}|MACD:{macd:.2f}|RSI:{rsi:.1f}"
        
        if not is_etf:
            eps = info.get('trailingEps', 'N/A')
            pe = info.get('trailingPE', 'N/A')
            pb = info.get('priceToBook', 'N/A')
            roe = info.get('returnOnEquity', 0) or 0
            g_m = info.get('grossMargins', 0) or 0
            o_m = info.get('operatingMargins', 0) or 0
            n_m = info.get('profitMargins', 0) or 0
            report += (f"\n【獲利】毛利:{g_m*100:.1f}%|營益:{o_m*100:.1f}%|稅後:{n_m*100:.1f}%\n"
                       f"【估值】EPS:{eps}|P/E:{pe}|P/B:{pb}|ROE:{roe*100:.1f}%")
        
        return report
                
    except Exception as e:
        return f"資料抓取異常: {e}"

def main():
    if not TOKEN:
        print("❌ 錯誤：找不到 LINE_TOKEN")
        return

    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*15]
    
    # 定義要追蹤的項目 (ETF 需設定 is_etf=True)
    targets = {
        '2330': {'name': '台積電', 'is_etf': False}, 
        '0050': {'name': '元大台灣50', 'is_etf': True},
        '00878': {'name': '國泰永續高股息', 'is_etf': True},
        '2454': {'name': '聯發科', 'is_etf': False},
        '2395': {'name': '研華', 'is_etf': False}
    }
    
    for sid, info in targets.items():
        data = get_stock_data(sid, info['is_etf'])
        report.append(f"【{info['name']}】\n{data}\n")
    
    report_text = "\n".join(report)
    
    # 發送邏輯 (同原代碼)
    payload = {"messages": [{"type": "text", "text": report_text}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    req = urllib.request.Request("https://api.line.me/v2/bot/message/broadcast", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"✅ 廣播成功！")
    except Exception as e:
        print(f"❌ 廣播失敗: {e}")

if __name__ == "__main__":
    main()
