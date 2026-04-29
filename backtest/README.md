# Backtest — Trend + RSI Strategy

Test your trading bot on real historical data BEFORE risking real money.

## Setup (one time)

```bash
pip install backtrader yfinance pandas matplotlib
```

## Run

```bash
python backtest.py
```

## See Results

Open `dashboard.html` in your browser after running the backtest.
Both files must be in the same folder.

## What to change in backtest.py

| Variable | Default | What it does |
|---|---|---|
| SYMBOL | RELIANCE.NS | Stock to test (.NS = NSE) |
| START_DATE | 2022-01-01 | Backtest from |
| END_DATE | 2024-12-31 | Backtest to |
| INITIAL_CAP | 100000 | Starting capital in ₹ |
| RSI_OVERSOLD | 30 | BUY signal threshold |
| RSI_OVERBOUGHT | 70 | SELL signal threshold |
| STOP_LOSS_PCT | 0.01 | 1% stop loss |
| TAKE_PROFIT_PCT | 0.02 | 2% take profit |

## What the results mean

| Metric | What's good |
|---|---|
| Sharpe Ratio | > 1.0 (> 2.0 is great) |
| Win Rate | > 50% |
| Max Drawdown | < 15% ideally |
| Profit Factor | > 1.5 |

## Other NSE stocks to test

- `TCS.NS`
- `HDFCBANK.NS`
- `INFY.NS`
- `WIPRO.NS`
- `ICICIBANK.NS`

## Only go live when:
1. Sharpe > 1.0
2. Win rate > 50%
3. Max drawdown < 20%
4. You've paper traded for 1-2 months
