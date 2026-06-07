# future-trading-bot
A professional-grade, multi-threaded Algorithmic Crypto Futures Trading Bot built with Python. This bot utilizes a 3-Way Confluence Strategy combined with Multi-Timeframe Analysis to scan markets, manage risks dynamically, and track performance via a live compound-interest simulator.

## ✨ Key Features

* Multi-Timeframe Trend Confluence:- Analyzes the macro trend on the `15m` chart (using EMA 21) and executes precise entries on the `1m` chart.
* 3-Way Indicator Strategy:- Combines Exponential Moving Averages (EMA 9/21 Cross), Relative Strength Index (RSI Pullbacks), and Volume Moving Average (10-period) to filter out fakeouts.
* Simultaneous Multi-Coin Scanning:- Scans multiple pairs (`SOLUSDT`, `ETHUSDT`, `BTCUSDT`, `BNBUSDT`) concurrently without pausing during active trades.
* Windows Desktop Notifications:- Sends real-time pop-up banner alerts and sound cues directly to your PC screen when a signal is detected, or a trade closes.
* Compound Interest Paper Trading Simulator:- Built-in simulation starting with a custom wallet size ($4.00) that reinvests profits automatically (Compounding Mode).
* Live Stats Dashboard:- Real-time terminal output displaying Starting Balance, Updated Live Balance, Total Wins/Losses, and Net Win Rate percentage.

## 🛠️ Tech Stack & Libraries

* Language:- Python 3.11.5
* IDE:- VS Code
* API Integration:- `python-binance` (Binance Official Client)
* Data Analysis:- `pandas`
* Alert System:- `plyer` (Native Windows Notifications)
* Network Requests:- `requests`
