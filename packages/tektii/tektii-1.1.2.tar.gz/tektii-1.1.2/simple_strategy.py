from decimal import Decimal
from typing import Optional

from tektii.strategy import TektiiStrategy
from tektii.strategy.models import (
    TickData,
    BarData,
    OrderUpdateEvent,
    PositionUpdateEvent,
    AccountUpdateEvent,
    OrderBuilder,
)


class SimpleMovingAverageStrategy(TektiiStrategy):
    """A strategy that opens trades on every market data event with TP/SL."""
    
    def __init__(self):
        super().__init__()
        self.position_size = Decimal("100")
        self.trade_counter = 0
        
        # Risk management parameters (as percentages) - 2:1 profit/loss ratio
        self.stop_loss_pct = Decimal("0.01")  # 0.1% stop loss (very small)
        self.take_profit_pct = Decimal("0.02")  # 0.2% take profit (2:1 ratio)
        
    def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None) -> None:
        """Open a trade with TP/SL on every market data event."""
        price = None
        symbol = None
        
        if tick_data and tick_data.last:
            price = float(tick_data.last)
            symbol = tick_data.symbol
        elif bar_data:
            price = float(bar_data.close)
            symbol = bar_data.symbol
            
        if price and symbol:
            # Open a trade on every event
            self.trade_counter += 1
            
            # Alternate between buy and sell orders
            is_buy = self.trade_counter % 2 == 1
            
            # Calculate protective order prices based on current price
            current_price = Decimal(str(price))
            
            if is_buy:
                # For buy orders: SL below, TP above
                stop_loss_price = current_price * (Decimal("1") - self.stop_loss_pct)
                take_profit_price = current_price * (Decimal("1") + self.take_profit_pct)
                
                self.logger.info(f"Opening BUY trade #{self.trade_counter} at ${current_price:.4f}")
                self.logger.info(f"  Stop Loss: ${stop_loss_price:.4f} (-{self.stop_loss_pct * 100}%)")
                self.logger.info(f"  Take Profit: ${take_profit_price:.4f} (+{self.take_profit_pct * 100}%)")
                
                order = (
                    OrderBuilder()
                    .symbol(symbol)
                    .buy()
                    .market()
                    .quantity(self.position_size)
                    .with_bracket(
                        stop_loss=stop_loss_price,
                        take_profit=take_profit_price
                    )
                    .build()
                )
            else:
                # For sell orders: SL above, TP below
                stop_loss_price = current_price * (Decimal("1") + self.stop_loss_pct)
                take_profit_price = current_price * (Decimal("1") - self.take_profit_pct)
                
                self.logger.info(f"Opening SELL trade #{self.trade_counter} at ${current_price:.4f}")
                self.logger.info(f"  Stop Loss: ${stop_loss_price:.4f} (+{self.stop_loss_pct * 100}%)")
                self.logger.info(f"  Take Profit: ${take_profit_price:.4f} (-{self.take_profit_pct * 100}%)")
                
                order = (
                    OrderBuilder()
                    .symbol(symbol)
                    .sell()
                    .market()
                    .quantity(self.position_size)
                    .with_bracket(
                        stop_loss=stop_loss_price,
                        take_profit=take_profit_price
                    )
                    .build()
                )
            
            order_id = self.place_order(order)
            if order_id:
                self.logger.info(f"Order placed successfully: {order_id}")
    
    def on_order_update(self, event: OrderUpdateEvent) -> None:
        """Handle order status updates."""
        self.logger.info(f"Order {event.order_id} status: {event.status}")
        
        # Track protective order executions
        if event.order_intent:
            if event.order_intent.value == "STOP_LOSS" and event.status.value == "FILLED":
                self.logger.warning(f"STOP LOSS TRIGGERED for {event.symbol} - Loss limited at ${event.fill_price}")
            elif event.order_intent.value == "TAKE_PROFIT" and event.status.value == "FILLED":
                self.logger.info(f"TAKE PROFIT REACHED for {event.symbol} - Profit captured at ${event.fill_price}")
    
    def on_position_update(self, event: PositionUpdateEvent) -> None:
        """Handle position updates."""
        self.logger.info(f"Position in {event.symbol}: {event.quantity} @ {event.average_price}")
    
    def on_account_update(self, event: AccountUpdateEvent) -> None:
        """Handle account balance updates."""
        self.logger.info(f"Account balance: ${event.cash_balance}")
    
    def on_initialize(self, config: dict, symbols: list) -> None:
        """Initialize the strategy with configuration."""
        super().on_initialize(config, symbols)
        
        # Allow configuration of strategy parameters
        if "position_size" in config:
            self.position_size = Decimal(config["position_size"])
        if "stop_loss_pct" in config:
            self.stop_loss_pct = Decimal(config["stop_loss_pct"])
        if "take_profit_pct" in config:
            self.take_profit_pct = Decimal(config["take_profit_pct"])
        
        self.logger.info("Strategy initialized with parameters:")
        self.logger.info(f"  Position Size: {self.position_size}")
        self.logger.info(f"  Stop Loss: {self.stop_loss_pct * 100}%, Take Profit: {self.take_profit_pct * 100}%")
        self.logger.info(f"  Profit/Loss Ratio: {self.take_profit_pct / self.stop_loss_pct}:1")