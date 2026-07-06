import yfinance as yf
import requests
import json
import time

TOKEN = "S9r44KFKxG8T+fcql+KHLGZ0fy2/zHEMsNgWY91thDIDQDjKYFhzVp215VjeX8uivL4CqYvYr2lhc8if7nj8jsIqDQTR8fHKel2ulRPxbJUO2iw6+O5NAYFLTiRKLgfh7AWrrV/bPiAWpDSDJ5AHZQdB04t89/1O/w1cDnyilFU=" # 記得換成你的 Token

def get_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(period="120d")
        if hist.empty: return "無歷史資料"

        close = hist['Close']
        price = close.iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        
        return (f"💰現價:{price:.0f}\n布林:{ma20-2*std20:.0f}~{ma20+2*std20:.0f}")
    except Exception as e:
        return f"錯誤: {str(e)}"

def main():
    stocks = {'2330': '台積電', '2454': '聯發科'}
    report = ["📊 技術分析報告"]
    for sid, sname in stocks.items():
        report.append(f"\n【{sname}】\n{get_data(sid)}")
    
    # 使用 requests 發送，比 urllib 更穩定
    url = "https://notify-api.line.me/api/notify"
    headers = {'Authorization': f'Bearer {TOKEN}'}
    data = {'message': "\n".join(report)}
    
    # 強制重試機制
    for i in range(3):
        try:
            res = requests.post(url, headers=headers, data=data, timeout=15)
            if res.status_code == 200:
                print("發送成功")
                break
        except Exception:
            if i == 2: raise
            time.sleep(5)

if __name__ == "__main__":
    main()
