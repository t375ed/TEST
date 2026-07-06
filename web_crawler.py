import pandas as pd # 請確認檔案開頭已匯入 pandas

def get_stock_data(stock_id):
    """
    功能：在原架構上，加入毛利、技術指標與估值數據
    """
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d")
        info = ticker.info
        
        # --- 數據獲取 ---
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 0)
        g_m = info.get('grossMargins', 0)
        o_m = info.get('operatingMargins', 0)
        n_m = info.get('profitMargins', 0)
        
        # --- 技術指標計算 ---
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
        
        # --- 區塊化排版 (嚴格依照你要求的順序) ---
        return (f"💰現價:{price}\n"
                f"【獲利】毛利:{g_m*100:.1f}%|營益:{o_m*100:.1f}%|稅後:{n_m*100:.1f}%\n"
                f"【技術】布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}|MACD:{macd:.2f}|RSI:{rsi:.1f}\n"
                f"【估值】EPS:{eps}|P/E:{pe}|P/B:{pb}|ROE:{roe*100:.1f}%")
                
    except Exception as e:
        print(f"DEBUG: 抓取 {stock_id} 失敗: {e}")
        return "資料抓取異常"
