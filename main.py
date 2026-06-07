import time
import os
import msvcrt
from plyer import notification
from src.binance_client import BinanceManager
from src.strategy import TradingStrategy
from src.paper_trader import PaperTrader

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def send_desktop_alert(title, message):
    """Windows Screen එකට කෙලින්ම Notification Pop-up එකක් යවන කෑල්ල"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Softrar Futures Bot",
            timeout=10
        )
    except Exception as e:
        print(f"❌ Desktop Alert Error: {e}")

def main():
    bot = BinanceManager()
    strategy = TradingStrategy()
    
    # 💡 $4.00 ACCOUNT SETUP (STARTING BALANCE)
    STARTING_BAL = 4.0
    paper = PaperTrader(initial_balance=STARTING_BAL) 
    
    symbols = ['SOLUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT'] 
    DELAY = 10     

    # FUTURES RISK MANAGEMENT SETTINGS
    LEVERAGE = 20           
    MARGIN_PER_TRADE = 1.0  # එක ට්‍රේඩ් එකකට ගන්නේ $1.00 යි
    STOP_LOSS_PCT = 1.5     
    TAKE_PROFIT_PCT = 3.0    

    clear_terminal()
    print("==========================================================")
    print("   🚀 SOFTRAR FUTURES BOT: MULTI-COIN MULTI-TASKING MODE  ")
    print("==========================================================")
    print(f"Leverage: {LEVERAGE}x | Margin/Trade: ${MARGIN_PER_TRADE}\n")
    
    send_desktop_alert("🚀 SOFTRAR BOT STARTED!", "Multi-Tasking මාදිලිය සක්‍රීයයි. සියලුම කොයින් ස්කෑන් කරමින් පවතී...")

    current_prices = {} 

    while True:
        print("\n" + "-"*60)
        print(f"🔍 [SCAN START] - {time.strftime('%X')} | Wallet: ${paper.get_report(0)['wallet_balance']:.2f}")
        print("-"*60)

        for symbol in symbols:
            try:
                # Multi-Timeframe දත්ත ලබා ගැනීම
                df_1m = bot.get_ohlcv(symbol, interval='1m', limit=50)
                df_15m = bot.get_ohlcv(symbol, interval='15m', limit=50)
                
                if df_1m.empty or df_15m.empty: continue
                
                signal = strategy.get_signal(df_1m, df_15m)
                current_price = df_1m['close'].iloc[-1]
                current_prices[symbol] = current_price

                # -----------------------------------------------------------------
                # ඒ වෙලාවේ මේ කොයින් එකේ ට්‍රේඩ් එකක් ලයිව් දුවනවා නම්
                # -----------------------------------------------------------------
                if paper.in_position and paper.symbol == symbol:
                    trigger = paper.check_sl_tp(current_price)
                    if trigger:
                        pnl_usd, pnl_pct = paper.calculate_pnl(current_price)
                        send_desktop_alert(
                            f"⚡ POSITION CLOSED ({trigger})",
                            f"Coin: {symbol} | PnL: ${pnl_usd:.2f} ({pnl_pct:.2f}%)"
                        )
                        paper.close_position(current_price, reason=trigger)
                        continue
                        
                    pnl_usd, pnl_pct = paper.calculate_pnl(current_price)
                    print(f"🔥 [ACTIVE POSITION] {symbol} | {paper.direction} {paper.leverage}x")
                    print(f"   Entry: ${paper.entry_price:.2f} -> Current: ${current_price:.2f} | PnL: {pnl_pct:.2f}% (${pnl_usd:.2f})")
                    print("   👉 Close කිරීමට 'q' ඔබන්න...")
                    
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'q':
                            send_desktop_alert("🛑 MANUAL EXIT", f"Coin: {symbol} | PnL: ${pnl_usd:.2f}")
                            paper.close_position(current_price, reason="MANUAL_EXIT")
                            continue

                # -----------------------------------------------------------------
                # වෙනත් කොයින් ස්කෑන් කිරීම (Simultaneous Scanning)
                # -----------------------------------------------------------------
                else:
                    print(f"🔍 Scanning {symbol:9} | Price: ${current_price:10.2f} | Signal: {signal}")

                    if signal in ["BUY", "SELL"]:
                        direction = "LONG" if signal == "BUY" else "SHORT"
                        
                        if paper.in_position:
                            # වෙනත් ට්‍රේඩ් එකක හිටියත් අලුත් අවස්ථාව ලැප් එකට නොටිෆිකේෂන් දෙනවා
                            send_desktop_alert(
                                f"💡 NEW SIGNAL OPPORTUNITY!",
                                f"{symbol} ({direction}) @ ${current_price} (දැනට ට්‍රේඩ් එකක් පවතින බැවින් මඟහැරියා)"
                            )
                            print(f"⚠️ [OPPORTUNITY] {symbol} {direction} සිග්නල් එකක් ආවා, නමුත් දැනටමත් ට්‍රේඩ් එකක් පවතින නිසා skip කළා.")
                        else:
                            # ට්‍රේඩ් එකක් නැත්නම් කෙලින්ම Alert එක දීලා අහනවා
                            send_desktop_alert(
                                f"🚨 PRO ALERT: {symbol} SIGNAL!",
                                f"Action: {direction} | Price: ${current_price}"
                            )
                            
                            print("\n" + "🎯"*15)
                            print(f"🚨 PRO ALERT: {symbol} {direction} CONFLUENCE FOUND!")
                            print("🎯"*15)
                            
                            user_input = input(f"👉 {direction} Trade එක කරන්නද? (Enter = YES / 'no' = SKIP): ")
                            if user_input.lower() != 'no':
                                success = paper.open_position(
                                    symbol=symbol, direction=direction, entry_price=current_price,
                                    margin=MARGIN_PER_TRADE, leverage=LEVERAGE,
                                    sl_pct=STOP_LOSS_PCT, tp_pct=TAKE_PROFIT_PCT
                                )
                                if success:
                                    send_desktop_alert("✅ POSITION OPENED!", f"Coin: {symbol} | Style: {direction}")
                                    print(f"✅ POSITION OPENED: {symbol} at ${current_price}\n")
                            else:
                                print("❌ SKIPPED: Trade එක මඟහැරියා.\n")

                time.sleep(1) 

            except Exception as e:
                print(f"Error on {symbol}: {e}")

        # Dashboard එක අප්ඩේට් කිරීම
        active_symbol_price = current_prices.get(paper.symbol, 0.0) if paper.in_position else 0.0
        report = paper.get_report(active_symbol_price)
        
        print("\n📊 ==================== SOFTRAR ACCOUNT DASHBOARD ====================")
        print(f"   💵 STARTING BALANCE:   ${STARTING_BAL:.2f}")
        print(f"   💰 UPDATED BALANCE:    ${report['wallet_balance']:.2f}  <-- Live/Compound 🔥")
        print(f"   💵 AVAILABLE USDT:     ${report['available_usdt']:.2f}")
        print(f"   ------------------------------------------------------------------")
        print(f"   🟢 Total Profits:      +${report['total_profit']:.2f} ({report['wins']} Wins)")
        print(f"   🔴 Total Losses:       -${report['total_loss']:.2f} ({report['losses']} Losses)")
        
        total_trades = report['wins'] + report['losses']
        win_rate = (report['wins'] / total_trades) * 100 if total_trades > 0 else 0.0
        print(f"   📈 Bot Win Rate:       {win_rate:.1f}% | Total Closed Trades: {total_trades}")
        print("======================================================================")
        
        print(f"Next scan in {DELAY} seconds...")
        time.sleep(DELAY)

if __name__ == "__main__":
    main()