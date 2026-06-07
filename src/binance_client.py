import pandas as pd
from binance.client import Client

class BinanceManager:
    def __init__(self):
        self.client = Client()

    def get_ohlcv(self, symbol, interval='1m', limit=100):
        try:
            # Timeframe එක අනුව කොච්චර පරණ Data ඕනෙද කියලා තීරණය කරමු
            start_str = "2 hours ago" if interval == '1m' else "24 hours ago"
            
            bars = self.client.futures_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str
            )
            
            if not bars: return pd.DataFrame()
            bars = bars[-limit:]

            df = pd.DataFrame(bars, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['open'] = df['open'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            return df
        except Exception as e:
            print(f"❌ Binance API Error ({symbol} - {interval}): {e}")
            return pd.DataFrame()