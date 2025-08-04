"""Mock broker implementation for testing strategies.

This module provides a mock implementation of the TektiiBroker service
that can be used for testing strategies without a real broker connection.
"""

from __future__ import annotations

import time
from typing import Dict

import grpc

from tektii.strategy.grpc import common_pb2, market_data_pb2, orders_pb2, service_pb2_grpc


class MockBrokerService(service_pb2_grpc.TektiiBrokerServicer):
    """Mock implementation of TektiiBroker for testing."""

    def __init__(self) -> None:
        """Initialize the mock broker."""
        self.positions: Dict[str, common_pb2.Position] = {}
        self.orders: Dict[str, common_pb2.Order] = {}
        self.account = common_pb2.AccountState(
            cash_balance=100000.0,
            portfolio_value=100000.0,
            buying_power=100000.0,
            initial_margin=0.0,
            maintenance_margin=0.0,
            margin_used=0.0,
            daily_pnl=0.0,
            total_pnl=0.0,
        )
        self.market_data: Dict[str, market_data_pb2.TickData] = {}
        self.order_counter = 0

    def GetState(self, request: orders_pb2.StateRequest, context: grpc.ServicerContext) -> orders_pb2.StateResponse:
        """Get current state snapshot."""
        response = orders_pb2.StateResponse()
        response.timestamp_us = int(time.time() * 1_000_000)

        if request.include_positions:
            for symbol, position in self.positions.items():
                if not request.symbols or symbol in request.symbols:
                    response.positions[symbol].CopyFrom(position)

        if request.include_orders:
            for order_id, order in self.orders.items():
                if not request.symbols or order.symbol in request.symbols:
                    response.orders[order_id].CopyFrom(order)

        if request.include_account:
            response.account.CopyFrom(self.account)

        return response

    def GetHistoricalData(
        self,
        request: market_data_pb2.HistoricalDataRequest,
        context: grpc.ServicerContext,
    ) -> market_data_pb2.HistoricalDataResponse:
        """Get historical bar data."""
        response = market_data_pb2.HistoricalDataResponse()
        response.symbol = request.symbol
        response.bar_size = request.bar_size

        # Generate mock historical data
        current_time = request.end_timestamp_us
        time_delta = 60_000_000  # 1 minute in microseconds

        bars_to_generate = min(request.limit, 100) if request.limit > 0 else 100
        base_price = 100.0

        for i in range(bars_to_generate):
            timestamp = current_time - (i * time_delta)
            if timestamp < request.start_timestamp_us:
                break

            # Simple random walk
            open_price = base_price + (i % 10) * 0.1
            high_price = open_price + 0.5
            low_price = open_price - 0.3
            close_price = open_price + 0.2

            bar = common_pb2.Bar(
                timestamp_us=timestamp,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=1000 + i * 10,
                vwap=(open_price + close_price) / 2,
            )
            response.bars.append(bar)

        # Return in chronological order
        bars_list = list(response.bars)
        bars_list.reverse()
        del response.bars[:]
        response.bars.extend(bars_list)
        return response

    def GetMarketDepth(
        self,
        request: market_data_pb2.MarketDepthRequest,
        context: grpc.ServicerContext,
    ) -> market_data_pb2.MarketDepthResponse:
        """Get current order book."""
        response = market_data_pb2.MarketDepthResponse()
        response.symbol = request.symbol
        response.timestamp_us = int(time.time() * 1_000_000)

        # Generate mock order book
        base_price = 100.0
        spread = 0.02

        for i in range(request.depth):
            # Bids (buy orders)
            bid_price = base_price - (i * 0.01) - spread / 2
            bid = common_pb2.PriceLevel(
                price=bid_price,
                size=1000.0 * (i + 1),
                order_count=i + 1,
            )
            response.bids.append(bid)

            # Asks (sell orders)
            ask_price = base_price + (i * 0.01) + spread / 2
            ask = common_pb2.PriceLevel(
                price=ask_price,
                size=1000.0 * (i + 1),
                order_count=i + 1,
            )
            response.asks.append(ask)

        return response

    def GetRiskMetrics(self, request: orders_pb2.RiskMetricsRequest, context: grpc.ServicerContext) -> orders_pb2.RiskMetricsResponse:
        """Get portfolio risk metrics."""
        response = orders_pb2.RiskMetricsResponse()
        response.timestamp_us = int(time.time() * 1_000_000)

        # Mock risk metrics
        response.portfolio_var = 1000.0
        response.portfolio_sharpe = 1.5
        response.portfolio_beta = 0.8
        response.max_drawdown = 0.15

        # Add position risks
        for symbol, position in self.positions.items():
            if not request.symbols or symbol in request.symbols:
                risk = common_pb2.PositionRisk(
                    symbol=symbol,
                    position_var=abs(position.quantity) * 10,
                    beta=0.9,
                    volatility=0.2,
                    exposure=position.market_value,
                )
                response.position_risks[symbol].CopyFrom(risk)

        return response

    def PlaceOrder(self, request: orders_pb2.PlaceOrderRequest, context: grpc.ServicerContext) -> orders_pb2.PlaceOrderResponse:
        """Place a new order."""
        response = orders_pb2.PlaceOrderResponse()

        # Simple validation
        if request.quantity <= 0:
            response.accepted = False
            response.reject_reason = "Invalid quantity"
            response.reject_code = common_pb2.REJECT_CODE_INVALID_QUANTITY
            return response

        # Generate order ID
        self.order_counter += 1
        order_id = f"TEST-{self.order_counter:06d}"

        # Create order
        order = common_pb2.Order(
            order_id=order_id,
            symbol=request.symbol,
            status=common_pb2.ORDER_STATUS_SUBMITTED,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            filled_quantity=0.0,
            limit_price=request.limit_price,
            stop_price=request.stop_price,
            created_at_us=int(time.time() * 1_000_000),
            order_intent=request.order_intent,
            parent_trade_id=request.parent_trade_id,
        )

        self.orders[order_id] = order

        # Success response
        response.accepted = True
        response.order_id = order_id
        response.request_id = request.request_id
        response.timestamp_us = int(time.time() * 1_000_000)
        response.estimated_fill_price = 100.0  # Mock price
        response.estimated_commission = 1.0

        return response

    def CancelOrder(self, request: orders_pb2.CancelOrderRequest, context: grpc.ServicerContext) -> orders_pb2.CancelOrderResponse:
        """Cancel an existing order."""
        response = orders_pb2.CancelOrderResponse()

        if request.order_id not in self.orders:
            response.accepted = False
            response.reject_reason = "Order not found"
            response.reject_code = common_pb2.REJECT_CODE_ORDER_NOT_FOUND
            return response

        order = self.orders[request.order_id]
        # Check if order can be cancelled
        if order.status in [
            common_pb2.ORDER_STATUS_FILLED,
            common_pb2.ORDER_STATUS_CANCELED,
            common_pb2.ORDER_STATUS_REJECTED,
        ]:
            response.accepted = False
            response.reject_reason = "Order cannot be cancelled in current state"
            response.reject_code = common_pb2.REJECT_CODE_ORDER_NOT_MODIFIABLE
            return response

        # Cancel the order
        response.accepted = True
        response.order_id = request.order_id
        response.request_id = request.request_id
        response.previous_status = order.status
        response.filled_quantity = order.filled_quantity
        response.timestamp_us = int(time.time() * 1_000_000)

        # Update order status
        order.status = common_pb2.ORDER_STATUS_CANCELED

        return response

    def ModifyOrder(self, request: orders_pb2.ModifyOrderRequest, context: grpc.ServicerContext) -> orders_pb2.ModifyOrderResponse:
        """Modify an existing order."""
        response = orders_pb2.ModifyOrderResponse()

        if request.order_id not in self.orders:
            response.accepted = False
            response.reject_reason = "Order not found"
            response.reject_code = common_pb2.REJECT_CODE_ORDER_NOT_FOUND
            return response

        order = self.orders[request.order_id]

        # Check if order can be modified
        if order.status not in [
            common_pb2.ORDER_STATUS_PENDING,
            common_pb2.ORDER_STATUS_SUBMITTED,
            common_pb2.ORDER_STATUS_ACCEPTED,
        ]:
            response.accepted = False
            response.reject_reason = "Order cannot be modified in current state"
            response.reject_code = common_pb2.REJECT_CODE_ORDER_NOT_MODIFIABLE
            return response

        # Apply modifications
        if request.HasField("quantity"):
            order.quantity = request.quantity.value
        if request.HasField("limit_price"):
            order.limit_price = request.limit_price.value
        if request.HasField("stop_price"):
            order.stop_price = request.stop_price.value

        response.accepted = True
        response.order_id = request.order_id
        response.request_id = request.request_id
        response.timestamp_us = int(time.time() * 1_000_000)

        return response

    def ValidateOrder(self, request: orders_pb2.ValidateOrderRequest, context: grpc.ServicerContext) -> orders_pb2.ValidateOrderResponse:
        """Validate an order without placing it."""
        response = orders_pb2.ValidateOrderResponse()
        response.request_id = request.request_id

        # Basic validation
        errors = []
        warnings = []

        if request.quantity <= 0:
            error = common_pb2.ValidationError(
                field="quantity",
                message="Quantity must be positive",
                code=common_pb2.VALIDATION_ERROR_INVALID_QUANTITY,
            )
            errors.append(error)

        if request.order_type == common_pb2.ORDER_TYPE_LIMIT and request.limit_price <= 0:
            error = common_pb2.ValidationError(
                field="limit_price",
                message="Limit price required for limit orders",
                code=common_pb2.VALIDATION_ERROR_INVALID_PRICE,
            )
            errors.append(error)

        # Mock warning
        if request.quantity > 10000:
            warning = common_pb2.ValidationWarning(
                field="quantity",
                message="Large order size",
                code=common_pb2.VALIDATION_WARNING_UNUSUAL_SIZE,
            )
            warnings.append(warning)

        response.valid = len(errors) == 0
        response.errors.extend(errors)
        response.warnings.extend(warnings)
        response.estimated_fill_price = 100.0
        response.estimated_market_impact = 0.01

        return response

    def ClosePosition(self, request: orders_pb2.ClosePositionRequest, context: grpc.ServicerContext) -> orders_pb2.ClosePositionResponse:
        """Close a position."""
        response = orders_pb2.ClosePositionResponse()

        if request.symbol not in self.positions:
            response.accepted = False
            response.reject_reason = "No position found"
            response.reject_code = common_pb2.REJECT_CODE_ORDER_NOT_FOUND
            return response

        position = self.positions[request.symbol]
        closing_quantity = request.quantity if request.quantity > 0 else position.quantity

        # Create closing order
        self.order_counter += 1
        order_id = f"TEST-{self.order_counter:06d}"

        response.accepted = True
        response.request_id = request.request_id
        response.order_ids.append(order_id)
        response.position_quantity = position.quantity
        response.closing_quantity = closing_quantity
        response.remaining_quantity = position.quantity - closing_quantity
        response.timestamp_us = int(time.time() * 1_000_000)

        return response

    def ModifyTradeProtection(
        self,
        request: orders_pb2.ModifyTradeProtectionRequest,
        context: grpc.ServicerContext,
    ) -> orders_pb2.ModifyTradeProtectionResponse:
        """Modify stop loss and take profit orders."""
        response = orders_pb2.ModifyTradeProtectionResponse()

        # Mock implementation
        response.accepted = True
        response.trade_id = request.trade_id
        response.request_id = request.request_id
        response.stop_loss_order_id = f"SL-{request.trade_id}"
        response.take_profit_order_id = f"TP-{request.trade_id}"
        response.trade_quantity = 100.0
        response.trade_entry_price = 100.0
        response.current_price = 101.0
        response.max_loss = 500.0
        response.max_profit = 1000.0
        response.timestamp_us = int(time.time() * 1_000_000)

        return response
