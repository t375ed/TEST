import yfinance as yf
from datetime import datetime, timezone, timedelta
import urllib.request
import json

# 設定區 (保持你的 Token 不變)
TOKEN = "S9r44KFKxG8T+fcql+KHLGZ0fy2/zHEMsNgWY91thDIDQDjKYFhzVp215VjeX8uivL4CqYvYr2lhc8if7nj8jsIqDQTR8fHKel2ulRPxbJUO2iw6+O5NAYFLTiRKLgfh7AWrrV/bPiAWpDSDJ5AHZQdB04t89/1O/w1cDnyilFU="
USER_ID = "U601a272f959493a2714777ec87256977"

def get_stock_data(stock_id):
    """
    功能：使用 yfinance 抓取股價、EPS 與財務指標
    """
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        info = ticker.info
        
        # 抓取數據，若抓不到則顯示 N/A
        price = info.get('currentPrice', 'N/A')
        eps = info.get('trailingEps', 'N/A')       # EPS
        pe = info.get('trailingPE', 'N/A')         # 本益比
        div_yield = info.get('dividendYield', 0)   # 殖利率
        
        # 格式化殖利率
        div_str = f"{div_yield*100:.2f}%" if div_yield else "N/A"
        
        return f"💰價:{price} | EPS:{eps}\nPE:{pe} | 殖利率:{div_str}"
    except Exception as e:
        print(f"DEBUG: 抓取 {stock_id} 失敗: {e}")
        return "資料抓取異常"

def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*15]
    
    stocks = {'2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    
    for sid, sname in stocks.items():
        data = get_stock_data(sid)
        report.append(f"【{sname}】\n{data}\n")
    
    report_text = "\n".join(report)
    
    # 發送至 LINE
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": report_text}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}
    
    req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                 data=json.dumps(payload).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req) as response:
        print("✅ 成功！")

if __name__ == "__main__":
    main()
