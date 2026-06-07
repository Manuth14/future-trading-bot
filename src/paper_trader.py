class PaperTrader:
    def __init__(self, initial_balance=100.0):
        self.initial_balance = initial_balance
        self.wallet_balance = initial_balance
        self.available_usdt = initial_balance
        
        # Position States
        self.in_position = False
        self.symbol = ""
        self.direction = ""  # "LONG" or "SHORT"
        self.entry_price = 0.0
        self.margin = 0.0
        self.leverage = 1
        self.stop_loss_price = 0.0
        self.take_profit_price = 0.0
        self.position_size_coin = 0.0

        # 📊 STATS TRACKING
        self.total_profit_usd = 0.0
        self.total_loss_usd = 0.0
        self.win_count = 0
        self.loss_count = 0

    def open_position(self, symbol, direction, entry_price, margin, leverage, sl_pct, tp_pct):
        if self.in_position:
            return False
        
        if margin > self.available_usdt:
            print("❌ Margin Error: Insufficient available USDT!")
            return False

        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.margin = margin
        self.leverage = leverage
        self.in_position = True

        self.available_usdt -= margin
        
        # Position Size ගණනය කිරීම (Margin x Leverage)
        position_value_usd = margin * leverage
        self.position_size_coin = position_value_usd / entry_price

        # Stop Loss සහ Take Profit මට්ටම් සැකසීම
        if direction == "LONG":
            self.stop_loss_price = entry_price * (1 - (sl_pct / 100))
            self.take_profit_price = entry_price * (1 + (tp_pct / 100))
        else: # SHORT
            self.stop_loss_price = entry_price * (1 + (sl_pct / 100))
            self.take_profit_price = entry_price * (1 - (tp_pct / 100))

        return True

    def calculate_pnl(self, current_price):
        if not self.in_position:
            return 0.0, 0.0
        
        price_diff = current_price - self.entry_price
        
        if self.direction == "LONG":
            pnl_usd = price_diff * self.position_size_coin
        else: # SHORT
            pnl_usd = -price_diff * self.position_size_coin

        pnl_pct = (pnl_usd / self.margin) * 100
        return pnl_usd, pnl_pct

    def check_sl_tp(self, current_price):
        if not self.in_position:
            return None

        if self.direction == "LONG":
            if current_price >= self.take_profit_price:
                return "TP"
            elif current_price <= self.stop_loss_price:
                return "SL"
        else: # SHORT
            if current_price <= self.take_profit_price:
                return "TP"
            elif current_price >= self.stop_loss_price:
                return "SL"
        
        return None

    def close_position(self, current_price, reason="MANUAL"):
        if not self.in_position:
            return

        pnl_usd, _ = self.calculate_pnl(current_price)
        
        # ට්‍රේඩ් එක වැහෙන කොට Stats Update කිරීම
        if pnl_usd >= 0:
            self.total_profit_usd += pnl_usd
            self.win_count += 1
        else:
            self.total_loss_usd += abs(pnl_usd)
            self.loss_count += 1

        # 💰 COMPOUNDING LOGIC: ප්‍රධාන Wallet Balance එක සැබැවින්ම අප්ඩේට් කිරීම
        self.wallet_balance += pnl_usd
        self.available_usdt = self.wallet_balance
        
        # Position එක Reset කිරීම
        self.in_position = False
        self.symbol = ""
        self.direction = ""
        self.entry_price = 0.0
        self.margin = 0.0
        self.stop_loss_price = 0.0
        self.take_profit_price = 0.0
        self.position_size_coin = 0.0

    def get_report(self, current_price=0.0):
        # ට්‍රේඩ් එකක් ලයිව් දුවනවා නම් ඒකෙ floating PnL එකත් එක්ක balance එක පෙන්වීමට
        live_wallet = self.wallet_balance
        if self.in_position and current_price > 0:
            pnl_usd, _ = self.calculate_pnl(current_price)
            live_wallet += pnl_usd

        return {
            "wallet_balance": live_wallet,
            "available_usdt": self.available_usdt,
            "total_profit": self.total_profit_usd,
            "total_loss": self.total_loss_usd,
            "wins": self.win_count,
            "losses": self.loss_count
        }