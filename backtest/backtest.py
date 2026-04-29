"""
backtest.py — Trend + RSI Strategy Backtester
============================================
Uses yfinance (free data) + backtrader (backtesting engine)

SETUP:
    pip install backtrader yfinance pandas matplotlib

RUN:
    python backtest.py

OUTPUT:
    - Prints full performance report
    - Saves results.json (open dashboard.html to visualize)
    - Shows equity curve chart
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
import json, sys
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIGURATION — edit these freely
# ─────────────────────────────────────────
SYMBOL          = "RELIANCE.NS"   # Yahoo Finance symbol (.NS = NSE India)
START_DATE      = "2022-01-01"
END_DATE        = "2024-12-31"
INITIAL_CAP     = 100_000         # Starting capital in ₹
COMMISSION      = 0.0003          # ~0.03% per trade (Zerodha approx)

SMA_FAST        = 50
SMA_SLOW        = 200
RSI_PERIOD      = 14
RSI_OVERSOLD    = 30
RSI_OVERBOUGHT  = 70

RISK_PER_TRADE  = 0.01    # Risk 1% of capital per trade
STOP_LOSS_PCT   = 0.01    # 1% stop loss
TAKE_PROFIT_PCT = 0.02    # 2% take profit (2:1 reward:risk)


# ─────────────────────────────────────────
#  STRATEGY
# ─────────────────────────────────────────
class TrendRSIStrategy(bt.Strategy):

    def __init__(self):
        self.sma_fast     = bt.indicators.SMA(self.data.close, period=SMA_FAST)
        self.sma_slow     = bt.indicators.SMA(self.data.close, period=SMA_SLOW)
        self.rsi          = bt.indicators.RSI(self.data.close, period=RSI_PERIOD)
        self.order        = None
        self.entry_price  = None
        self.stop_price   = None
        self.target_price = None
        self.trade_log    = []
        self.equity_curve = []

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price  = order.executed.price
                self.stop_price   = self.entry_price * (1 - STOP_LOSS_PCT)
                self.target_price = self.entry_price * (1 + TAKE_PROFIT_PCT)
            self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trade_log.append({
                "date":    self.data.datetime.date(0).isoformat(),
                "pnl":     round(trade.pnl, 2),
                "pnlcomm": round(trade.pnlcomm, 2),
                "won":     trade.pnl > 0,
            })

    def next(self):
        self.equity_curve.append({
            "date":   self.data.datetime.date(0).isoformat(),
            "equity": round(self.broker.getvalue(), 2),
        })

        if self.order:
            return

        price = self.data.close[0]

        if self.position:
            if price <= self.stop_price or price >= self.target_price:
                self.close()
            return

        capital  = self.broker.getvalue()
        risk_amt = capital * RISK_PER_TRADE
        qty      = int(risk_amt / (price * STOP_LOSS_PCT))
        if qty < 1:
            return

        bullish = self.sma_fast[0] > self.sma_slow[0] and self.rsi[0] < RSI_OVERSOLD
        bearish = self.sma_fast[0] < self.sma_slow[0] and self.rsi[0] > RSI_OVERBOUGHT

        if bullish:
            self.order = self.buy(size=qty)
        elif bearish:
            self.order = self.sell(size=qty)


# ─────────────────────────────────────────
#  RUNNER
# ─────────────────────────────────────────
def run():
    print(f"\n  Downloading {SYMBOL} data {START_DATE} to {END_DATE}...")
    raw = yf.download(SYMBOL, start=START_DATE, end=END_DATE,
                      interval="1d", auto_adjust=True, progress=False)

    if raw.empty:
        print(f"No data for {SYMBOL}. Try adding .NS for NSE stocks e.g. RELIANCE.NS")
        sys.exit(1)

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0].lower() for c in raw.columns]
    else:
        raw.columns = [c.lower() for c in raw.columns]

    raw.index = pd.to_datetime(raw.index)
    print(f"  Got {len(raw)} daily candles\n")

    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=raw))
    cerebro.addstrategy(TrendRSIStrategy)
    cerebro.broker.setcash(INITIAL_CAP)
    cerebro.broker.setcommission(commission=COMMISSION)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,  _name='sharpe',
                        riskfreerate=0.065, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown,      _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    start_val = cerebro.broker.getvalue()
    results   = cerebro.run()
    end_val   = cerebro.broker.getvalue()
    strat     = results[0]

    sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio') or 0
    dd     = strat.analyzers.drawdown.get_analysis()
    ta     = strat.analyzers.trades.get_analysis()

    won          = ta.get('won',  {}).get('total', 0)
    lost         = ta.get('lost', {}).get('total', 0)
    total_trades = won + lost
    win_rate     = (won / total_trades * 100) if total_trades > 0 else 0
    avg_win      = ta.get('won',  {}).get('pnl', {}).get('average', 0)
    avg_loss     = ta.get('lost', {}).get('pnl', {}).get('average', 0)
    profit_factor = abs(avg_win / avg_loss) if avg_loss else 0
    total_return  = (end_val - start_val) / start_val * 100
    years         = (pd.Timestamp(END_DATE) - pd.Timestamp(START_DATE)).days / 365
    cagr          = ((end_val / start_val) ** (1 / years) - 1) * 100 if years > 0 else 0
    max_dd        = dd.get('max', {}).get('drawdown', 0)

    print("=" * 52)
    print("       BACKTEST RESULTS — TREND + RSI BOT")
    print("=" * 52)
    print(f"  Symbol          : {SYMBOL}")
    print(f"  Period          : {START_DATE}  to  {END_DATE}")
    print(f"  Initial Capital : Rs {INITIAL_CAP:,.0f}")
    print(f"  Final Capital   : Rs {end_val:,.2f}")
    print(f"  Total Return    : {total_return:+.2f}%")
    print(f"  CAGR            : {cagr:.2f}% per year")
    print(f"  Sharpe Ratio    : {sharpe:.3f}  (>1.0 = good, >2.0 = great)")
    print(f"  Max Drawdown    : {max_dd:.2f}%  (how much you lost at worst)")
    print(f"  Total Trades    : {total_trades}")
    print(f"  Win Rate        : {win_rate:.1f}%")
    print(f"  Profit Factor   : {profit_factor:.2f}  (>1.5 = acceptable)")
    print(f"  Avg Win         : Rs {avg_win:.2f}")
    print(f"  Avg Loss        : Rs {avg_loss:.2f}")
    print("=" * 52)

    print("\n  VERDICT:")
    if sharpe and sharpe > 1.0 and win_rate > 50:
        print("  GOOD — worth paper trading 1-2 months before going live")
    elif total_return > 0:
        print("  MARGINAL — needs optimization. Do NOT go live yet.")
    else:
        print("  FAILED — strategy lost money. Do NOT trade live.")

    print("\n  WHAT TO TRY NEXT:")
    print("  1. Change RSI levels to 20/80 (stricter signals)")
    print("  2. Change SMA to 20/50 (faster signals)")
    print("  3. Test other symbols: TCS.NS, HDFCBANK.NS, INFY.NS")
    print("  4. Only go live if: Sharpe > 1.0 AND win rate > 50%\n")

    output = {
        "symbol": SYMBOL, "start": START_DATE, "end": END_DATE,
        "initial_capital": INITIAL_CAP,
        "final_capital": round(end_val, 2),
        "total_return_pct": round(total_return, 2),
        "cagr_pct": round(cagr, 2),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown_pct": round(max_dd, 2),
        "total_trades": total_trades,
        "winning_trades": won,
        "losing_trades": lost,
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": round(profit_factor, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "equity_curve": strat.equity_curve,
        "trades": strat.trade_log,
    }

    with open("results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("  Saved results.json — open dashboard.html to see charts!\n")
    cerebro.plot(style='candlestick', barup='green', bardown='red')


if __name__ == "__main__":
    run()
