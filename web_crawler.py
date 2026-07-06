import yfinance as yf
import urllib.request
import urllib.parse
import json
import time

# 請填入你的真實 LINE Notify Token
TOKEN = "填入你的真實TOKEN" 

def get_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d")
        if hist.empty: return "無歷史資料"

        close = hist['Close']
        price = close.iloc[-1]
        
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = ema12 - ema26
        
        return (f"💰現價:{price:.0f} | MACD:{macd:.2f}\n"
                f"布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}")
    except Exception as e:
        return f"計算錯誤: {str(e)}"

def main():
    stocks = {'2330': '台積電', '2454': '聯發科'}
    report = ["📊 實戰技術分析報告"]
    for sid, sname in stocks.items():
        report.append(f"\n【{sname}】\n{get_data(sid)}")
    
    # 增加重試機制
    payload = {"message": "\n".join(report)}
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/x-www-form-urlencoded'}
    
    for i in range(3): # 最多嘗試 3 次
        try:
            req = urllib.request.Request("https://notify-api.line.me/api/notify", 
                                         data=urllib.parse.urlencode(payload).encode('utf-8'), headers=headers)
            urllib.request.urlopen(req, timeout=10)
            break 
        except Exception as e:
            if i == 2: raise e
            time.sleep(5)

if __name__ == "__main__":
    main()
