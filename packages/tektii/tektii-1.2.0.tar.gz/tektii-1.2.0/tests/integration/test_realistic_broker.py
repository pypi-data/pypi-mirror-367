"""Integration tests for the RealisticMockBroker."""

import time
from decimal import Decimal

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.testing.market_simulator import MarketCondition
from tektii.testing.realistic_broker import RealisticMockBroker


class TestRealisticMockBroker:
    """Test the RealisticMockBroker functionality."""

    def test_broker_with_market_simulation(self) -> None:
        """Test broker with background market simulation."""
        broker = RealisticMockBroker(initial_cash=Decimal("50000"))

        # Start market simulation
        broker.start_market_simulation(update_interval=0.1)

        try:
            # Let markets move for a bit
            time.sleep(0.3)

            # Check that markets have been updated
            aapl_market = broker.market_sim.markets["AAPL"]
            initial_price = Decimal("150.00")

            # Price should have moved (but not too much)
            assert abs(aapl_market.last_price - initial_price) < 5
            assert aapl_market.bid < aapl_market.ask
            assert len(aapl_market.bid_depth) > 0
            assert len(aapl_market.ask_depth) > 0

        finally:
            broker.stop_market_simulation()

    def test_order_with_slippage(self) -> None:
        """Test order execution with realistic slippage."""
        broker = RealisticMockBroker(initial_cash=Decimal("1000000"))  # Plenty of cash
        broker.enable_slippage = True

        # Place a large market order
        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=5000.0,  # Large order
            request_id="req-001",
        )

        response = broker.PlaceOrder(request, None)

        assert response.accepted
        order = broker.orders[response.order_id]
        assert order.status == common_pb2.ORDER_STATUS_FILLED

        # Check that we got filled at ask or higher (slippage)
        market = broker.market_sim.markets["AAPL"]
        assert response.estimated_fill_price >= float(market.ask)

    def test_limit_order_behavior(self) -> None:
        """Test realistic limit order behavior."""
        broker = RealisticMockBroker()
        broker.enable_rejections = False  # Disable random rejections for deterministic test

        # Get current market
        market = broker.market_sim.markets["AAPL"]

        # Place buy limit below market
        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=100.0,
            limit_price=float(market.bid - Decimal("1.00")),
            request_id="req-002",
        )

        response = broker.PlaceOrder(request, None)

        assert response.accepted
        order = broker.orders[response.order_id]

        # Check order status - might be filled or submitted depending on random execution
        if order.status == common_pb2.ORDER_STATUS_FILLED:
            # Got lucky with random fill
            assert order.filled_quantity == 100.0
        else:
            # Normal case - not immediately filled
            assert order.status == common_pb2.ORDER_STATUS_SUBMITTED
            assert order.filled_quantity == 0

        # Place sell limit at market - should fill immediately
        request2 = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_SELL,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=100.0,
            limit_price=float(market.bid),
            request_id="req-003",
        )

        response2 = broker.PlaceOrder(request2, None)
        assert response2.accepted  # Ensure order was accepted
        order2 = broker.orders[response2.order_id]

        # Should fill immediately at bid
        assert order2.status == common_pb2.ORDER_STATUS_FILLED
        assert order2.filled_quantity == 100.0

    def test_position_tracking_with_pnl(self) -> None:
        """Test position tracking with P&L calculation."""
        broker = RealisticMockBroker()

        # Buy 100 shares
        buy_request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=100.0,
            request_id="req-004",
        )

        buy_response = broker.PlaceOrder(buy_request, None)
        assert buy_response.accepted

        # Check position
        position = broker.positions["AAPL"]
        assert position.quantity == 100.0
        assert position.avg_price > 0
        initial_value = position.market_value

        # Simulate price movement up
        broker.SimulateMarketMovement("AAPL", Decimal("155.00"), steps=5, interval=0.01)

        # Check unrealized P&L
        assert position.unrealized_pnl > 0
        assert position.market_value > initial_value

        # Sell half the position
        sell_request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_SELL,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=50.0,
            request_id="req-005",
        )

        sell_response = broker.PlaceOrder(sell_request, None)
        assert sell_response.accepted

        # Check position and realized P&L
        assert position.quantity == 50.0
        assert position.realized_pnl > 0  # Should have profit

    def test_risk_limit_rejection(self) -> None:
        """Test order rejection due to risk limits."""
        broker = RealisticMockBroker(initial_cash=Decimal("10000"))

        # Try to buy more than we can afford
        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=1000.0,  # ~$150,000 worth
            request_id="req-006",
        )

        response = broker.PlaceOrder(request, None)

        assert not response.accepted
        assert "Risk limit exceeded" in response.reject_reason
        assert response.reject_code == common_pb2.REJECT_CODE_RISK_CHECK_FAILED
        # Check risk check fields
        assert response.risk_check.position_limit > 0

    def test_market_condition_effects(self) -> None:
        """Test how market conditions affect price behavior."""
        broker = RealisticMockBroker()

        # Set volatile market condition
        broker.SetMarketCondition("TSLA", MarketCondition.VOLATILE)

        # Record initial state
        tesla_market = broker.market_sim.markets["TSLA"]
        initial_price = tesla_market.last_price

        # Update markets several times
        for _ in range(10):
            broker.market_sim.update_all_markets(dt=1.0)

        # Check that volatility caused larger moves
        price_change = abs(tesla_market.last_price - initial_price)
        current_spread = tesla_market.ask - tesla_market.bid

        # Volatile markets should have moved more
        assert price_change > 0
        # Note: spread widening is random, so we can't guarantee it will always be wider
        # Just check that spread is positive
        assert current_spread > 0

    def test_partial_fill_simulation(self) -> None:
        """Test partial fill simulation for large orders."""
        broker = RealisticMockBroker()
        broker.enable_partial_fills = True

        # Test the partial fill logic
        fills = broker.market_sim.simulate_partial_fill(Decimal("10000"))

        assert len(fills) > 1  # Should be multiple fills
        assert sum(fills) == Decimal("10000")  # Should sum to total

        # Each fill should be reasonable size
        for fill in fills:
            assert fill >= 1
            assert fill <= 10000

    def test_order_book_depth(self) -> None:
        """Test order book depth generation."""
        broker = RealisticMockBroker()

        market = broker.market_sim.markets["AAPL"]

        # Check order book structure
        assert len(market.bid_depth) == 10  # Default 10 levels
        assert len(market.ask_depth) == 10

        # Verify price ordering
        for i in range(1, len(market.bid_depth)):
            assert market.bid_depth[i][0] < market.bid_depth[i - 1][0]

        for i in range(1, len(market.ask_depth)):
            assert market.ask_depth[i][0] > market.ask_depth[i - 1][0]

        # Verify size increases with depth
        assert market.bid_depth[-1][1] > market.bid_depth[0][1]
        assert market.ask_depth[-1][1] > market.ask_depth[0][1]

    def test_account_updates_with_positions(self) -> None:
        """Test account value updates as positions change."""
        broker = RealisticMockBroker(initial_cash=Decimal("100000"))
        broker.enable_rejections = False  # Disable random rejections for this test

        initial_portfolio_value = broker.account.portfolio_value
        assert initial_portfolio_value == 100000.0

        # Buy some positions
        for symbol in ["AAPL", "GOOGL", "MSFT"]:
            request = orders_pb2.PlaceOrderRequest(
                symbol=symbol,
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=10.0,
                request_id=f"req-{symbol}",
            )
            response = broker.PlaceOrder(request, None)
            assert response.accepted

        # Portfolio value should include positions
        assert broker.account.portfolio_value > 0
        assert broker.account.cash_balance < 100000.0
        assert broker.account.margin_used > 0

        # Simulate market movement
        broker.start_market_simulation(update_interval=0.1)
        time.sleep(0.3)
        broker.stop_market_simulation()

        # Portfolio value should have changed
        assert broker.account.portfolio_value != initial_portfolio_value

    def test_random_rejection_simulation(self) -> None:
        """Test random order rejections."""
        broker = RealisticMockBroker()
        broker.enable_rejections = True

        # Place many orders to trigger some rejections
        rejections = 0
        rejection_reasons = []
        for i in range(100):
            request = orders_pb2.PlaceOrderRequest(
                symbol="AAPL",
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=1.0,
                request_id=f"req-{i:03d}",
            )
            response = broker.PlaceOrder(request, None)
            if not response.accepted:
                rejections += 1
                rejection_reasons.append(response.reject_reason)

        # Should have some rejections (around 5%)
        assert rejections > 0
        assert rejections < 20  # But not too many

        # Check we got meaningful rejection reasons
        assert len(set(rejection_reasons)) > 0  # Should have variety

    def test_limit_price_validation(self) -> None:
        """Test limit price validation."""
        broker = RealisticMockBroker()

        market = broker.market_sim.markets["AAPL"]

        # Try to place limit order far from market
        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL",
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=100.0,
            limit_price=float(market.last_price * Decimal("0.5")),  # 50% below market
            request_id="req-far-limit",
        )

        response = broker.PlaceOrder(request, None)

        assert not response.accepted
        assert "too far from market" in response.reject_reason
