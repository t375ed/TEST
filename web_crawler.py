import urllib.request
import json
import ssl
from datetime import datetime, timezone, timedelta

# ========================================================
# 設定區
# ========================================================
TOKEN = "S9r44KFKxG8T+fcql+KHLGZ0fy2/zHEMsNgWY91thDIDQDjKYFhzVp215VjeX8uivL4CqYvYr2lhc8if7nj8jsIqDQTR8fHKel2ulRPxbJUO2iw6+O5NAYFLTiRKLgfh7AWrrV/bPiAWpDSDJ5AHZQdB04t89/1O/w1cDnyilFU="
USER_ID = "U601a272f959493a2714777ec87256977"

def get_stock_price(stock_id):
    """
    功能：透過 Yahoo Finance 抓取股價 (穩定繞過 403 限制)
    注意：台股代號需加上 '.TW' 後綴
    """
    # Yahoo Finance 網址結構
    symbol = f"{stock_id}.TW"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            data = json.loads(response.read().decode())
            # 解析 JSON 結構中的最新收盤價
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return str(price)
    except Exception as e:
        print(f"DEBUG: 抓取 {symbol} 失敗: {e}")
    return None

def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    report = [f"📊 股市收盤報告 ({now.strftime('%m/%d %H:%M')})", "-"*15]
    
    # 注意：代號後方不需要加 .TW，程式會自動處理
    stocks = {'0050': '元大台灣50', '2330': '台積電', '2454': '聯發科', '2395': '研華', '2327': '國巨'}
    
    for sid, sname in stocks.items():
        price = get_stock_price(sid)
        report.append(f"{sname}: {price if price else '目前無報價'}")
    
    report_text = "\n".join(report)
    
    # 發送
    clean_token = TOKEN.strip().encode('ascii', 'ignore').decode('ascii')
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": report_text}]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {clean_token}'}
    
    try:
        req = urllib.request.Request("https://api.line.me/v2/bot/message/push", 
                                     data=json.dumps(payload).encode('utf-8'), 
                                     headers=headers)
        with urllib.request.urlopen(req) as response:
            print("✅ 成功！已從 Yahoo Finance 抓取並推送。")
    except Exception as e:
        print(f"❌ 發送失敗: {e}")

if __name__ == "__main__":
    main()
