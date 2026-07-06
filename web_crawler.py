import yfinance as yf
import urllib.request
import json

# 請直接將你的 Token 填入這裡，確保發送成功
TOKEN = "S9r44KFKxG8T+fcql+KHLGZ0fy2/zHEMsNgWY91thDIDQDjKYFhzVp215VjeX8uivL4CqYvYr2lhc8if7nj8jsIqDQTR8fHKel2ulRPxbJUO2iw6+O5NAYFLTiRKLgfh7AWrrV/bPiAWpDSDJ5AHZQdB04t89/1O/w1cDnyilFU=" 

def get_data(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        info = ticker.info
        hist = ticker.history(period="60d")
        
        # 1. 基本面數據 (直接從 info 讀取，如果 info 有資料就會顯示)
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        div_yield = info.get('dividendYield', 0)
        if div_yield: div_yield = f"{div_yield*100:.2f}%"
        else: div_yield = "N/A"

        # 2. 技術指標計算
        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        upper = ma20 + (2 * std20)
        lower = ma20 - (2 * std20)

        return (f"💰現價:{price} | EPS:{eps} | PE:{pe}\n"
                f"殖利率:{div_yield}\n"
                f"布林:上{upper:.0f} 中{ma20:.0f} 下{lower:.0f}")
    except Exception as e:
        return f"資料抓取異常: {str(e)}"

def main():
    stocks = {'2330': '台積電', '2454': '聯發科'}
    report = ["📊 完整數據報告"]
    
    for sid, sname in stocks.items():
        data = get_data(sid)
        report.append(f"\n【{sname}】\n{data}")
    
    payload = {"message": "\n".join(report)}
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib.request.Request("https://notify-api.line.me/api/notify", 
                                 data=urllib.parse.urlencode(payload).encode('utf-8'), headers=headers)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    main()
