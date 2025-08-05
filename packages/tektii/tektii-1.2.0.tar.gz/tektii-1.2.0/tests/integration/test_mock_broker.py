"""Integration tests for the MockBrokerService."""

import time

from tektii.strategy.grpc import common_pb2, market_data_pb2, orders_pb2
from tektii.testing.mock_broker import MockBrokerService


class TestMockBrokerService:
    """Test the MockBrokerService functionality."""

    def test_broker_initialization(self) -> None:
        """Test broker initializes with correct defaults."""
        broker = MockBrokerService()

        assert broker.positions == {}
        assert broker.orders == {}
        assert broker.account.cash_balance == 100000.0
        assert broker.account.portfolio_value == 100000.0
        assert broker.account.buying_power == 100000.0
        assert broker.order_counter == 0

    def test_place_order_success(self) -> None:
        """Test successful order placement."""
        broker = MockBrokerService()

        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=100.0,
            request_id="req-001",
        )

        response = broker.PlaceOrder(request, None)

        assert response.accepted
        assert response.order_id == "TEST-000001"
        assert response.request_id == "req-001"
        assert response.estimated_fill_price == 100.0
        assert response.estimated_commission == 1.0

        # Verify order was created
        assert "TEST-000001" in broker.orders
        order = broker.orders["TEST-000001"]
        assert order.symbol == "AAPL"
        assert order.side == common_pb2.ORDER_SIDE_BUY
        assert order.quantity == 100.0
        assert order.status == common_pb2.ORDER_STATUS_SUBMITTED

    def test_place_order_validation_failure(self) -> None:
        """Test order placement with invalid quantity."""
        broker = MockBrokerService()

        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=-100.0,  # Invalid negative quantity
            request_id="req-002",
        )

        response = broker.PlaceOrder(request, None)

        assert not response.accepted
        assert response.reject_reason == "Invalid quantity"
        assert response.reject_code == common_pb2.REJECT_CODE_INVALID_QUANTITY
        assert len(broker.orders) == 0

    def test_cancel_order_success(self) -> None:
        """Test successful order cancellation."""
        broker = MockBrokerService()

        # First place an order
        place_request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=100.0,
            limit_price=150.0,
            request_id="req-003",
        )
        place_response = broker.PlaceOrder(place_request, None)
        order_id = place_response.order_id

        # Cancel the order
        cancel_request = orders_pb2.CancelOrderRequest(
            order_id=order_id,
            request_id="req-004",
        )
        cancel_response = broker.CancelOrder(cancel_request, None)

        assert cancel_response.accepted
        assert cancel_response.order_id == order_id
        assert cancel_response.previous_status == common_pb2.ORDER_STATUS_SUBMITTED

        # Verify order status was updated
        order = broker.orders[order_id]
        assert order.status == common_pb2.ORDER_STATUS_CANCELED

    def test_cancel_order_not_found(self) -> None:
        """Test cancelling non-existent order."""
        broker = MockBrokerService()

        cancel_request = orders_pb2.CancelOrderRequest(
            order_id="FAKE-ORDER",
            request_id="req-005",
        )
        cancel_response = broker.CancelOrder(cancel_request, None)

        assert not cancel_response.accepted
        assert cancel_response.reject_reason == "Order not found"
        assert cancel_response.reject_code == common_pb2.REJECT_CODE_ORDER_NOT_FOUND

    def test_cancel_filled_order(self) -> None:
        """Test cancelling already filled order."""
        broker = MockBrokerService()

        # Create a filled order
        order_id = "TEST-FILLED"
        broker.orders[order_id] = common_pb2.Order(
            order_id=order_id,
            symbol="AAPL",
            status=common_pb2.ORDER_STATUS_FILLED,
            quantity=100.0,
            filled_quantity=100.0,
        )

        cancel_request = orders_pb2.CancelOrderRequest(
            order_id=order_id,
            request_id="req-006",
        )
        cancel_response = broker.CancelOrder(cancel_request, None)

        assert not cancel_response.accepted
        assert "cannot be cancelled" in cancel_response.reject_reason
        assert cancel_response.reject_code == common_pb2.REJECT_CODE_ORDER_NOT_MODIFIABLE

    def test_modify_order_success(self) -> None:
        """Test successful order modification."""
        broker = MockBrokerService()

        # Place a limit order
        place_request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=100.0,
            limit_price=150.0,
            request_id="req-007",
        )
        place_response = broker.PlaceOrder(place_request, None)
        order_id = place_response.order_id

        # Import wrappers for DoubleValue
        from google.protobuf import wrappers_pb2

        # Modify the order
        modify_request = orders_pb2.ModifyOrderRequest(
            order_id=order_id,
            quantity=wrappers_pb2.DoubleValue(value=200.0),
            limit_price=wrappers_pb2.DoubleValue(value=155.0),
            request_id="req-008",
        )
        modify_response = broker.ModifyOrder(modify_request, None)

        assert modify_response.accepted
        assert modify_response.order_id == order_id

        # Verify order was modified
        order = broker.orders[order_id]
        assert order.quantity == 200.0
        assert order.limit_price == 155.0

    def test_validate_order(self) -> None:
        """Test order validation."""
        broker = MockBrokerService()

        # Valid order
        valid_request = orders_pb2.ValidateOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=100.0,
            limit_price=150.0,
            request_id="req-009",
        )
        valid_response = broker.ValidateOrder(valid_request, None)

        assert valid_response.valid
        assert len(valid_response.errors) == 0
        assert valid_response.estimated_fill_price == 100.0

        # Invalid order - negative quantity
        invalid_request = orders_pb2.ValidateOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=-100.0,
            limit_price=150.0,
            request_id="req-010",
        )
        invalid_response = broker.ValidateOrder(invalid_request, None)

        assert not invalid_response.valid
        assert len(invalid_response.errors) == 1
        assert invalid_response.errors[0].field == "quantity"
        assert invalid_response.errors[0].code == common_pb2.VALIDATION_ERROR_INVALID_QUANTITY

        # Order with warning - large quantity
        warning_request = orders_pb2.ValidateOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=15000.0,
            request_id="req-011",
        )
        warning_response = broker.ValidateOrder(warning_request, None)

        assert warning_response.valid
        assert len(warning_response.warnings) == 1
        assert warning_response.warnings[0].field == "quantity"
        assert warning_response.warnings[0].code == common_pb2.VALIDATION_WARNING_UNUSUAL_SIZE

    def test_get_state(self) -> None:
        """Test getting broker state."""
        broker = MockBrokerService()

        # Add some test data
        broker.positions["AAPL"] = common_pb2.Position(
            symbol="AAPL",
            quantity=100.0,
            avg_price=150.0,
            market_value=15000.0,
        )

        broker.orders["TEST-001"] = common_pb2.Order(
            order_id="TEST-001",
            symbol="AAPL",
            status=common_pb2.ORDER_STATUS_FILLED,
            quantity=100.0,
        )

        # Request all state
        request = orders_pb2.StateRequest(
            include_positions=True,
            include_orders=True,
            include_account=True,
        )
        response = broker.GetState(request, None)

        assert len(response.positions) == 1
        assert "AAPL" in response.positions
        assert response.positions["AAPL"].quantity == 100.0

        assert len(response.orders) == 1
        assert "TEST-001" in response.orders

        assert response.account.cash_balance == 100000.0

    def test_get_state_with_symbol_filter(self) -> None:
        """Test getting state with symbol filter."""
        broker = MockBrokerService()

        # Add positions for multiple symbols
        broker.positions["AAPL"] = common_pb2.Position(symbol="AAPL", quantity=100.0)
        broker.positions["GOOGL"] = common_pb2.Position(symbol="GOOGL", quantity=50.0)
        broker.positions["MSFT"] = common_pb2.Position(symbol="MSFT", quantity=75.0)

        # Request state for specific symbols
        request = orders_pb2.StateRequest(
            include_positions=True,
            symbols=["AAPL", "MSFT"],
        )
        response = broker.GetState(request, None)

        assert len(response.positions) == 2
        assert "AAPL" in response.positions
        assert "MSFT" in response.positions
        assert "GOOGL" not in response.positions

    def test_get_historical_data(self) -> None:
        """Test getting historical bar data."""
        broker = MockBrokerService()

        end_time = int(time.time() * 1_000_000)
        start_time = end_time - (3600 * 1_000_000)  # 1 hour ago

        request = market_data_pb2.HistoricalDataRequest(
            symbol="AAPL",
            bar_size="1_MINUTE",  # String representation of bar size
            start_timestamp_us=start_time,
            end_timestamp_us=end_time,
            limit=10,
        )
        response = broker.GetHistoricalData(request, None)

        assert response.symbol == "AAPL"
        assert response.bar_size == "1_MINUTE"
        assert len(response.bars) == 10

        # Verify bars are in chronological order
        for i in range(1, len(response.bars)):
            assert response.bars[i].timestamp_us > response.bars[i - 1].timestamp_us

        # Verify bar data
        first_bar = response.bars[0]
        assert first_bar.open > 0
        assert first_bar.high >= first_bar.open
        assert first_bar.low <= first_bar.open
        assert first_bar.close > 0
        assert first_bar.volume > 0

    def test_get_market_depth(self) -> None:
        """Test getting market depth (order book)."""
        broker = MockBrokerService()

        request = market_data_pb2.MarketDepthRequest(
            symbol="AAPL",
            depth=5,
        )
        response = broker.GetMarketDepth(request, None)

        assert response.symbol == "AAPL"
        assert len(response.bids) == 5
        assert len(response.asks) == 5

        # Verify bid prices decrease
        for i in range(1, len(response.bids)):
            assert response.bids[i].price < response.bids[i - 1].price

        # Verify ask prices increase
        for i in range(1, len(response.asks)):
            assert response.asks[i].price > response.asks[i - 1].price

        # Verify bid/ask spread
        assert response.asks[0].price > response.bids[0].price

    def test_get_risk_metrics(self) -> None:
        """Test getting risk metrics."""
        broker = MockBrokerService()

        # Add some positions
        broker.positions["AAPL"] = common_pb2.Position(
            symbol="AAPL",
            quantity=100.0,
            market_value=15000.0,
        )
        broker.positions["GOOGL"] = common_pb2.Position(
            symbol="GOOGL",
            quantity=50.0,
            market_value=10000.0,
        )

        request = orders_pb2.RiskMetricsRequest()
        response = broker.GetRiskMetrics(request, None)

        assert response.portfolio_var == 1000.0
        assert response.portfolio_sharpe == 1.5
        assert response.portfolio_beta == 0.8
        assert response.max_drawdown == 0.15

        assert len(response.position_risks) == 2
        assert "AAPL" in response.position_risks
        assert "GOOGL" in response.position_risks

        # Verify position risk calculations
        aapl_risk = response.position_risks["AAPL"]
        assert aapl_risk.position_var == 1000.0  # 100 * 10
        assert aapl_risk.exposure == 15000.0

    def test_close_position(self) -> None:
        """Test closing a position."""
        broker = MockBrokerService()

        # Add a position
        broker.positions["AAPL"] = common_pb2.Position(
            symbol="AAPL",
            quantity=100.0,
            avg_price=150.0,
        )

        # Close the position
        request = orders_pb2.ClosePositionRequest(
            symbol="AAPL",
            request_id="req-012",
        )
        response = broker.ClosePosition(request, None)

        assert response.accepted
        assert response.position_quantity == 100.0
        assert response.closing_quantity == 100.0
        assert response.remaining_quantity == 0.0
        assert len(response.order_ids) == 1
        assert response.order_ids[0] == "TEST-000001"

    def test_close_position_partial(self) -> None:
        """Test partially closing a position."""
        broker = MockBrokerService()

        # Add a position
        broker.positions["AAPL"] = common_pb2.Position(
            symbol="AAPL",
            quantity=100.0,
            avg_price=150.0,
        )

        # Close half the position
        request = orders_pb2.ClosePositionRequest(
            symbol="AAPL",
            quantity=50.0,
            request_id="req-013",
        )
        response = broker.ClosePosition(request, None)

        assert response.accepted
        assert response.position_quantity == 100.0
        assert response.closing_quantity == 50.0
        assert response.remaining_quantity == 50.0

    def test_close_position_not_found(self) -> None:
        """Test closing non-existent position."""
        broker = MockBrokerService()

        request = orders_pb2.ClosePositionRequest(
            symbol="FAKE",
            request_id="req-014",
        )
        response = broker.ClosePosition(request, None)

        assert not response.accepted
        assert response.reject_reason == "No position found"
        assert response.reject_code == common_pb2.REJECT_CODE_ORDER_NOT_FOUND

    def test_modify_trade_protection(self) -> None:
        """Test modifying stop loss and take profit orders."""
        broker = MockBrokerService()

        # The proto structure for ModifyTradeProtectionRequest is more complex
        # For now, we'll create a simpler request
        request = orders_pb2.ModifyTradeProtectionRequest(
            trade_id="TRADE-001",
            request_id="req-015",
        )
        response = broker.ModifyTradeProtection(request, None)

        assert response.accepted
        assert response.trade_id == "TRADE-001"
        assert response.stop_loss_order_id == "SL-TRADE-001"
        assert response.take_profit_order_id == "TP-TRADE-001"
        assert response.max_loss == 500.0
        assert response.max_profit == 1000.0

    def test_concurrent_order_placement(self) -> None:
        """Test placing multiple orders concurrently."""
        broker = MockBrokerService()

        # Place multiple orders
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        order_ids = []

        for i, symbol in enumerate(symbols):
            request = orders_pb2.PlaceOrderRequest(
                symbol=symbol,
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=100.0 + i * 10,
                request_id=f"req-{i:03d}",
            )
            response = broker.PlaceOrder(request, None)
            assert response.accepted
            order_ids.append(response.order_id)

        # Verify all orders were created with unique IDs
        assert len(set(order_ids)) == len(symbols)
        assert len(broker.orders) == len(symbols)

        # Verify order counter incremented correctly
        assert broker.order_counter == len(symbols)
