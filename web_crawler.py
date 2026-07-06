def get_stock_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        info = ticker.info
        hist = ticker.history(period="120d")
        
        # 基礎變數
        price = info.get('currentPrice', 'N/A')
        
        # --- 1. 獲利能力區 (財報) ---
        # 注意：部分個股若無即時財報欄位，會顯示為 N/A
        gross_margin = info.get('grossMargins', 0)
        op_margin = info.get('operatingMargins', 0)
        net_margin = info.get('profitMargins', 0)
        
        # --- 2. 技術面區 ---
        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = ema12 - ema26
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 3. 估值與核心指標區 ---
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 0)

        return (f"💰現價:{price}\n"
                f"【獲利能力】\n"
                f"毛利:{gross_margin*100:.1f}% | 營益:{op_margin*100:.1f}% | 稅後:{net_margin*100:.1f}%\n"
                f"【技術指標】\n"
                f"布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f} | MACD:{macd:.2f} | RSI:{rsi:.1f}\n"
                f"【估值指標】\n"
                f"EPS:{eps} | P/E:{pe} | P/B:{pb} | ROE:{roe*100:.1f}%")
                
    except Exception as e:
        return f"資料異常: {str(e)}"
