import yfinance as yf
import urllib.request
import urllib.parse
import json

# 請填入你的 LINE Notify Token
TOKEN = "填入你的真實TOKEN" 

def get_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        # 抓取 120 天數據，確保計算均線足夠
        hist = ticker.history(period="120d")
        if hist.empty: return "無歷史資料"

        close = hist['Close']
        price = close.iloc[-1]
        
        # 1. 技術指標計算 (布林、MACD、RSI)
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = ema12 - ema26
        
        # 2. 簡易估算 (若無法抓到財報，以技術面為準)
        # 既然 info 不穩，這裡直接呈現技術分析核心數據
        return (f"💰現價:{price:.0f}\n"
                f"布林軌道:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}\n"
                f"MACD:{macd:.2f}\n"
                f"20日均線:{ma20:.0f}")
    except Exception as e:
        return f"計算錯誤: {str(e)}"

def main():
    stocks = {'2330': '台積電', '2454': '聯發科'}
    report = ["📊 實戰技術分析報告"]
    for sid, sname in stocks.items():
        report.append(f"\n【{sname}】\n{get_data(sid)}")
    
    # 使用 LINE Notify 發送
    payload = {"message": "\n".join(report)}
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib.request.Request("https://notify-api.line.me/api/notify", 
                                 data=urllib.parse.urlencode(payload).encode('utf-8'), headers=headers)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    main()
