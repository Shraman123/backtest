# 📈 Algo Trading Bot — Trend + RSI Strategy

> A fully automated NSE trading bot built on Zerodha Kite, with a backtesting engine and visual dashboard.

---

## ⚡ What This Does

Monitors live NSE stocks every 5 minutes and auto-places orders when:

- **BUY** → SMA50 > SMA200 (uptrend) AND RSI < 30 (oversold)
- **SELL** → SMA50 < SMA200 (downtrend) AND RSI > 70 (overbought)

Built-in risk management: position sizing, stop loss, take profit.

---

## 🗂 Project Structure

```
trading_bot/
├── config.py              # All settings — edit this first
├── main.py                # Entry point — runs the live bot
├── strategy/
│   └── trend_rsi.py       # SMA + RSI signal logic
├── risk/
│   └── risk_manager.py    # Position sizing calculator
├── execution/
│   └── zerodha.py         # Kite order placement
├── data/
│   └── data_fetcher.py    # Historical data fetcher
└── utils/
    └── logger.py          # Trade log writer
```

---

## 🔧 Setup

### 1. Install dependencies

```bash
pip install kiteconnect pandas
```

### 2. Configure

Edit `config.py`:

```python
API_KEY    = "your_zerodha_api_key"
API_SECRET = "your_zerodha_api_secret"
SYMBOL     = "RELIANCE"
QUANTITY   = 1
```

### 3. Authenticate

```bash
# Zerodha requires a daily login
# After OAuth login, paste your access token:
kite.set_access_token("YOUR_ACCESS_TOKEN")
```

### 4. Run

```bash
python main.py
```

---

## 🧪 Backtest First (Seriously)

Test the strategy on historical data before risking real money.

```bash
cd backtest/
pip install backtrader yfinance pandas matplotlib
python backtest.py
```

Then open `dashboard.html` in your browser — you'll see:

- Equity curve
- Win/loss breakdown
- PnL per trade
- Full trade log

### Only go live when:

| Metric | Target |
|--------|--------|
| Sharpe Ratio | > 1.0 |
| Win Rate | > 50% |
| Max Drawdown | < 15% |
| Profit Factor | > 1.5 |

---

## ⚙️ Strategy Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SMA_FAST` | 50 | Fast moving average |
| `SMA_SLOW` | 200 | Slow moving average |
| `RSI_PERIOD` | 14 | RSI lookback period |
| `RSI_OVERSOLD` | 30 | BUY trigger threshold |
| `RSI_OVERBOUGHT` | 70 | SELL trigger threshold |
| `STOP_LOSS_PCT` | 1% | Max loss per trade |
| `TAKE_PROFIT_PCT` | 2% | Target per trade |
| `RISK_PER_TRADE` | 1% | Capital risked per trade |

---

## ⚠️ Disclaimer

This bot is for **educational purposes only**.

- Past backtest performance does not guarantee future returns
- Algo trading involves substantial risk of loss
- Always paper trade before using real capital
- Never risk money you cannot afford to lose

---

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Zerodha](https://img.shields.io/badge/Broker-Zerodha%20Kite-orange?style=flat-square)
![Backtrader](https://img.shields.io/badge/Backtesting-Backtrader-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

*Built for learning. Trade responsibly.*
  
