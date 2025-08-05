"""Base strategy class for Tektii Strategy SDK.

This module provides the base class that all trading strategies should inherit from.
It handles event routing, state management, and communication with the trading system.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import grpc

from tektii.strategy.grpc import orders_pb2
from tektii.strategy.models import (
    AccountState,
    AccountUpdateEvent,
    BarData,
    Order,
    OrderUpdateEvent,
    Position,
    PositionUpdateEvent,
    SystemEvent,
    TickData,
    TradeEvent,
)

logger = logging.getLogger(__name__)


class TektiiStrategy(ABC):
    """Base class for all Tektii trading strategies.

    This class provides the foundation for building trading strategies that
    communicate via gRPC with external trading systems. Strategies should
    inherit from this class and must implement the on_market_data method.
    All other event handlers are optional and have sensible defaults.

    Minimal Example:
        ```python
        from tektii.strategy import TektiiStrategy
        from tektii.strategy.models import TickData

        class MyStrategy(TektiiStrategy):
            def on_market_data(self, tick_data: TickData) -> None:
                if tick_data and tick_data.last > 100:
                    # Use self._broker_stub to place orders
                    pass
        ```

    Advanced Example (with optional methods):
        ```python
        from tektii.strategy import TektiiStrategy
        from tektii.strategy.models import TickData, OrderUpdateEvent, OrderStatus
        import logging

        logger = logging.getLogger(__name__)

        class AdvancedStrategy(TektiiStrategy):
            def on_initialize(self, config: Dict[str, str], symbols: List[str]) -> None:
                self.threshold = float(config.get("threshold", "100"))

            def on_market_data(self, tick_data: TickData) -> None:
                if tick_data and tick_data.last > self.threshold:
                    # Use self._broker_stub to place orders
                    pass

            def on_order_update(self, order_update: OrderUpdateEvent) -> None:
                if order_update.status == OrderStatus.FILLED:
                    logger.info(f"Order {order_update.order_id} filled")
        ```
    """

    def __init__(self) -> None:
        """Initialize the strategy."""
        self._positions: Dict[str, Position] = {}
        self._orders: Dict[str, Order] = {}
        self._account: Optional[AccountState] = None
        self._initialized = False
        self._config: Dict[str, str] = {}
        self._symbols: List[str] = []
        self._strategy_id: str = ""
        self._broker_stub: Optional[Any] = None  # TektiiBrokerStub - will be set by service if broker available
        self._broker_available = False
        self.logger = logger

    def _set_broker_stub(self, stub: object) -> None:
        """Set the broker stub for order management.

        This is called internally by the service when initializing.

        Args:
            stub: The gRPC stub for the broker service
        """
        self._broker_stub = stub
        self._broker_available = stub is not None
        if self._broker_available:
            logger.info("Broker stub set - order placement enabled")
        else:
            logger.warning("No broker stub - running in observation mode")

    # Public API - Override these methods in your strategy

    @abstractmethod
    def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None) -> None:
        """Handle market data events.

        Override this method to implement your strategy's response to market data.
        Either tick_data or bar_data will be provided, not both.

        Args:
            tick_data: Tick data (bid/ask/last prices)
            bar_data: Bar data (OHLCV)
        """
        pass

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:  # noqa: B027
        """Handle order update events.

        Override this method to react to order status changes.

        Args:
            order_update: Order update event
        """
        pass

    def on_position_update(self, position_update: PositionUpdateEvent) -> None:  # noqa: B027
        """Handle position update events.

        Override this method to react to position changes.

        Args:
            position_update: Position update event
        """
        pass

    def on_account_update(self, account_update: AccountUpdateEvent) -> None:  # noqa: B027
        """Handle account update events.

        Override this method to react to account balance changes.

        Args:
            account_update: Account update event
        """
        pass

    def on_trade(self, trade: TradeEvent) -> None:  # noqa: B027
        """Handle trade execution events.

        Override this method to react to trade executions.

        Args:
            trade: Trade event
        """
        pass

    def on_system_event(self, system_event: SystemEvent) -> None:  # noqa: B027
        """Handle system events.

        Override this method to react to system events like connection status.

        Args:
            system_event: System event
        """
        pass

    def on_initialize(self, config: Dict[str, str], symbols: List[str]) -> None:  # noqa: B027
        """Initialize the strategy.

        Override this method to set up your strategy state.

        Args:
            config: Configuration parameters
            symbols: List of symbols the strategy will trade
        """
        pass

    def on_shutdown(self) -> None:  # noqa: B027
        """Shut down the strategy.

        Override this method to clean up resources.
        """
        pass

    # Internal methods called by the service

    def _handle_event(self, event: orders_pb2.TektiiEvent) -> None:
        """Handle an incoming event from the service.

        This method is called by the service to dispatch events.

        Args:
            event: The event to handle
        """
        try:
            # Check which field is set in the oneof
            field = event.WhichOneof("event")

            if field == "tick_data":
                self.on_market_data(tick_data=TickData.from_proto(event.tick_data))
            elif field == "bar_data":
                self.on_market_data(bar_data=BarData.from_proto(event.bar_data))
            elif field == "order_update":
                # Update internal order tracking if we maintain state
                self.on_order_update(OrderUpdateEvent.from_proto(event.order_update))
            elif field == "position_update":
                # Update internal position tracking
                position_update = PositionUpdateEvent.from_proto(event.position_update)
                if position_update.quantity == 0:
                    self._positions.pop(position_update.symbol, None)
                else:
                    # Convert to Position for internal tracking
                    position = Position(
                        symbol=position_update.symbol,
                        quantity=position_update.quantity,
                        avg_price=position_update.avg_price,
                        market_value=position_update.market_value,
                        unrealized_pnl=position_update.unrealized_pnl,
                        realized_pnl=position_update.realized_pnl,
                        current_price=position_update.current_price,
                    )
                    self._positions[position_update.symbol] = position
                self.on_position_update(position_update)
            elif field == "account_update":
                # Update internal account state
                account_update = AccountUpdateEvent.from_proto(event.account_update)
                self._account = AccountState(
                    cash_balance=account_update.cash_balance,
                    portfolio_value=account_update.portfolio_value,
                    buying_power=account_update.buying_power,
                    initial_margin=account_update.initial_margin,
                    maintenance_margin=account_update.maintenance_margin,
                    margin_used=account_update.margin_used,
                    daily_pnl=account_update.daily_pnl,
                    total_pnl=account_update.total_pnl,
                )
                self.on_account_update(account_update)
            elif field == "trade":
                self.on_trade(TradeEvent.from_proto(event.trade))
            elif field == "system":
                self.on_system_event(SystemEvent.from_proto(event.system))
            else:
                logger.warning(f"Unknown event type: {field}")

        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)

    def _initialize(self, config: Dict[str, str], symbols: List[str], strategy_id: str) -> None:
        """Initialize the strategy internally.

        This is called by the service during initialization.

        Args:
            config: Configuration parameters
            symbols: List of symbols to trade
            strategy_id: Unique identifier for this strategy instance
        """
        self._config = config
        self._symbols = symbols
        self._strategy_id = strategy_id
        self._initialized = True

        try:
            self.on_initialize(config, symbols)
        except Exception as e:
            logger.error(f"Error in on_initialize: {e}", exc_info=True)
            raise

    def _shutdown(self) -> None:
        """Shut down the strategy internally.

        This is called by the service during shutdown.
        """
        try:
            self.on_shutdown()
        except Exception as e:
            logger.error(f"Error in on_shutdown: {e}", exc_info=True)
        finally:
            self._initialized = False

    # Helper methods for safe broker interactions

    @property
    def is_broker_available(self) -> bool:
        """Check if broker is available for placing orders.

        Returns:
            True if broker is connected and available
        """
        return self._broker_available and self._broker_stub is not None

    def place_order(self, order: Order) -> Optional[str]:
        """Safely place an order with the broker.

        This method handles broker availability checks and error handling.

        Args:
            order: The order to place

        Returns:
            Order ID if successful, None if failed or broker unavailable
        """
        if not self.is_broker_available:
            logger.warning(f"Cannot place order - broker not available. Would place: {order.side} {order.quantity} {order.symbol}")
            return None

        try:
            if self._broker_stub is None:
                logger.error("Broker stub is None - this should not happen")
                return None
            logger.debug(f"Placing order via broker stub: {order.side} {order.quantity} {order.symbol}")
            response = self._broker_stub.PlaceOrder(order)
            if response.accepted:
                logger.info(f"Order placed successfully: {response.order_id}")
                return str(response.order_id)
            else:
                logger.warning(f"Order rejected: {response.reject_reason}")
                return None
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                logger.error(f"Broker connection lost while placing order: {e.details()}")
                # Connection manager will handle reconnection automatically
                # Don't permanently disable broker - just return None for this attempt
            else:
                logger.error(f"gRPC error placing order: code={e.code()}, details={e.details()}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error placing order: {e}", exc_info=True)
            return None
