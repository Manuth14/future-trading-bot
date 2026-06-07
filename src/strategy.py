import pandas as pd

class TradingStrategy:
    def __init__(self):
        pass

    def get_signal(self, df_1m, df_15m):
        if len(df_1m) < 30 or len(df_15m) < 30:
            return "HOLD"

        # --- 15m MACRO TREND ANALYSIS ---
        # 15m එකේ Trend එක බලන්න සරලවම EMA 21 පාවිච්චි කරමු
        df_15m['EMA_21'] = df_15m['close'].ewm(span=21, adjust=False).mean()
        current_price_15m = df_15m['close'].iloc[-1]
        macro_ema_21 = df_15m['EMA_21'].iloc[-1]
        
        # මිල EMA 21 ට උඩින් තියෙනවා නම් ප්‍රධාන මාකට් එක Bullish, පල්ලෙහා නම් Bearish
        macro_trend = "BULLISH" if current_price_15m > macro_ema_21 else "BEARISH"

        # --- 1m EXECUTION ANALYSIS ---
        # 1m එකේ අපේ හොඳම Indicators 3 ගණනය කරමු
        change = df_1m['close'].diff()
        gain = change.mask(change < 0, 0)
        loss = -change.mask(change > 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean().replace(0, 0.00001)
        df_1m['RSI'] = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        df_1m['EMA_9'] = df_1m['close'].ewm(span=9, adjust=False).mean()
        df_1m['EMA_21'] = df_1m['close'].ewm(span=21, adjust=False).mean()
        df_1m['VOLUME_MA'] = df_1m['volume'].rolling(window=10).mean()

        rsi = df_1m['RSI'].iloc[-1]
        ema_9 = df_1m['EMA_9'].iloc[-1]
        ema_21 = df_1m['EMA_21'].iloc[-1]
        volume = df_1m['volume'].iloc[-1]
        volume_ma = df_1m['VOLUME_MA'].iloc[-1]

        # --- PRO CONFLUENCE LOGIC ---
        # LONG (BUY) වෙන්නේ 15m Trend එක උඩට තියෙද්දී, 1m එකේ Short-term Pullback එකක් ආවොත් විතරයි
        is_long = (
            macro_trend == "BULLISH" and # 👈 15m Confirmation
            ema_9 > ema_21 and 
            rsi < 48 and 
            volume > volume_ma
        )

        # SHORT (SELL) වෙන්නේ 15m Trend එක පල්ලෙහාට තියෙද්දී, 1m එකේ Short-term Rally එකක් ආවොත් විතරයි
        is_short = (
            macro_trend == "BEARISH" and # 👈 15m Confirmation
            ema_9 < ema_21 and 
            rsi > 52 and 
            volume > volume_ma
        )

        if is_long: return "BUY"
        elif is_short: return "SELL"
        return "HOLD"