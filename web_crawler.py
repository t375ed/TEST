def get_stock_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        info = ticker.info
        hist = ticker.history(period="120d")
        
        # 抓取數據 (若失敗則顯示 N/A 或 0)
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 0)
        gross_margin = info.get('grossMargins', 0)
        op_margin = info.get('operatingMargins', 0)
        net_margin = info.get('profitMargins', 0)
        
        # 技術指標計算 (布林/MACD)
        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = ema12 - ema26
        
        # 整理報告 (三大區塊)
        return (f"💰現價:{price}\n"
                f"【獲利】毛利:{gross_margin*100:.1f}%|營益:{op_margin*100:.1f}%|稅後:{net_margin*100:.1f}%\n"
                f"【技術】布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}|MACD:{macd:.2f}\n"
                f"【估值】EPS:{eps}|P/E:{pe}|P/B:{pb}|ROE:{roe*100:.1f}%")
                
    except Exception as e:
        return f"資料抓取異常: {str(e)}"
