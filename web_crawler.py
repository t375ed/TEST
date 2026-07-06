import yfinance as yf
import pandas as pd

# 直接計算核心數據，不依賴會出錯的 info API，也不透過網路發送
def get_full_analysis(stock_id):
    ticker = yf.Ticker(f"{stock_id}.TW")
    hist = ticker.history(period="120d")
    
    if hist.empty:
        return "無歷史資料"

    close = hist['Close']
    price = close.iloc[-1]
    
    # 技術指標計算
    ma20 = close.rolling(20).mean().iloc[-1]
    std20 = close.rolling(20).std().iloc[-1]
    ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
    macd = ema12 - ema26
    rsi_delta = close.diff()
    gain = (rsi_delta.where(rsi_delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-rsi_delta.where(rsi_delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rsi = 100 - (100 / (1 + (gain / loss)))

    # 顯示結果
    print(f"--- {stock_id} 完整分析 ---")
    print(f"當前市價: {price:.2f} 元")
    print(f"布林通道: 中軌 {ma20:.2f} | 上軌 {ma20+2*std20:.2f} | 下軌 {ma20-2*std20:.2f}")
    print(f"MACD指標: {macd:.3f}")
    print(f"RSI14指標: {rsi:.2f}")
    print("--------------------------")

def main():
    stocks = ['2330', '2454', '2395', '2327']
    for sid in stocks:
        get_full_analysis(sid)

if __name__ == "__main__":
    main()
