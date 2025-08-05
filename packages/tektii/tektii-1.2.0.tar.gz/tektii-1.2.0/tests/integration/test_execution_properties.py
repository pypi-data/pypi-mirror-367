"""Property-based tests for order execution and position tracking invariants."""

from decimal import Decimal

from hypothesis import assume, given
from hypothesis import strategies as st

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.testing.realistic_broker import RealisticMockBroker


class TestExecutionProperties:
    """Property-based tests for execution invariants."""

    @given(
        initial_cash=st.decimals(min_value=Decimal("1000"), max_value=Decimal("1000000"), places=2),
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("1"), max_value=Decimal("100"), places=0),
        price=st.decimals(min_value=Decimal("1"), max_value=Decimal("1000"), places=2),
    )
    def test_cash_balance_invariant(self, initial_cash: Decimal, symbol: str, quantity: Decimal, price: Decimal) -> None:
        """Test that cash balance changes correctly with trades."""
        broker = RealisticMockBroker(initial_cash=initial_cash)
        broker.enable_rejections = False  # Disable rejections for property testing

        # Add symbol to market
        broker.market_sim.add_symbol(symbol, price)

        initial_balance = Decimal(str(broker.account.cash_balance))

        # Place a buy order
        buy_request = orders_pb2.PlaceOrderRequest(
            symbol=symbol,
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=float(quantity),
        )
        buy_response = broker.PlaceOrder(buy_request, None)

        if buy_response.accepted:
            # Market buy orders execute at ask price
            market = broker.market_sim.markets[symbol]
            exec_price = market.ask

            # Cash should decrease by (quantity * exec_price + commission)
            expected_cash = initial_balance - (quantity * exec_price + Decimal("1.0"))
            actual_cash = Decimal(str(broker.account.cash_balance))

            # Allow for small rounding differences
            assert abs(actual_cash - expected_cash) <= Decimal("0.02")

            # Portfolio value should remain approximately the same (cash + positions)
            position_value = Decimal(str(broker.positions[symbol].market_value))
            total_value = actual_cash + position_value

            # Total value should be initial cash minus commissions
            # Note: small rounding differences can occur due to float conversions
            # Use relative tolerance for larger values
            tolerance = max(Decimal("0.01"), initial_balance * Decimal("0.0001"))
            assert abs(total_value - (initial_balance - Decimal("1.0"))) <= tolerance

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantities=st.lists(st.decimals(min_value=Decimal("1"), max_value=Decimal("100"), places=0), min_size=2, max_size=10),
        price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
    )
    def test_position_quantity_accumulation(self, symbol: str, quantities: list, price: Decimal) -> None:
        """Test that position quantities accumulate correctly."""
        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol to market
        broker.market_sim.add_symbol(symbol, price)

        total_quantity = Decimal("0")

        # Place multiple buy orders
        for qty in quantities:
            request = orders_pb2.PlaceOrderRequest(
                symbol=symbol,
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=float(qty),
            )
            response = broker.PlaceOrder(request, None)

            if response.accepted:
                total_quantity += qty

                # Check position quantity
                if symbol in broker.positions:
                    position_qty = Decimal(str(broker.positions[symbol].quantity))
                    assert abs(position_qty - total_quantity) < Decimal("0.01")

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        buy_quantity=st.decimals(min_value=Decimal("10"), max_value=Decimal("500"), places=0),
        sell_quantity=st.decimals(min_value=Decimal("1"), max_value=Decimal("500"), places=0),
        buy_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
        sell_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
    )
    def test_position_reduction_invariant(
        self, symbol: str, buy_quantity: Decimal, sell_quantity: Decimal, buy_price: Decimal, sell_price: Decimal
    ) -> None:
        """Test that selling reduces position correctly."""
        assume(sell_quantity <= buy_quantity)  # Can't sell more than we have
        assume(buy_quantity <= 500)  # Stay well within position limits

        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol to market at buy price
        broker.market_sim.add_symbol(symbol, buy_price)

        # Buy first
        buy_request = orders_pb2.PlaceOrderRequest(
            symbol=symbol,
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=float(buy_quantity),
        )
        buy_response = broker.PlaceOrder(buy_request, None)
        assert buy_response.accepted

        # Update market price for sell
        broker.market_sim.markets[symbol].last_price = sell_price
        broker.market_sim.markets[symbol].bid = sell_price - Decimal("0.01")
        broker.market_sim.markets[symbol].ask = sell_price + Decimal("0.01")

        # Sell some or all
        sell_request = orders_pb2.PlaceOrderRequest(
            symbol=symbol,
            side=common_pb2.ORDER_SIDE_SELL,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=float(sell_quantity),
        )
        sell_response = broker.PlaceOrder(sell_request, None)
        assert sell_response.accepted

        # Check remaining position
        expected_remaining = buy_quantity - sell_quantity
        actual_remaining = Decimal(str(broker.positions[symbol].quantity))
        assert abs(actual_remaining - expected_remaining) < Decimal("0.01")

        # If position is closed, average price should be reset
        if expected_remaining == 0:
            assert broker.positions[symbol].avg_price == 0.0

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        orders=st.lists(
            st.tuples(
                st.sampled_from([common_pb2.ORDER_SIDE_BUY, common_pb2.ORDER_SIDE_SELL]),
                st.decimals(min_value=Decimal("1"), max_value=Decimal("100"), places=0),
                st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
            ),
            min_size=1,
            max_size=20,
        ),
    )
    def test_order_id_uniqueness(self, symbol: str, orders: list) -> None:
        """Test that all order IDs are unique."""
        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol to market
        broker.market_sim.add_symbol(symbol, Decimal("100"))

        order_ids = set()

        for side, quantity, price in orders:
            # Update market price
            broker.market_sim.markets[symbol].last_price = price
            broker.market_sim.markets[symbol].bid = price - Decimal("0.01")
            broker.market_sim.markets[symbol].ask = price + Decimal("0.01")

            request = orders_pb2.PlaceOrderRequest(
                symbol=symbol,
                side=side,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=float(quantity),
            )
            response = broker.PlaceOrder(request, None)

            if response.accepted:
                # Order ID should be unique
                assert response.order_id not in order_ids
                order_ids.add(response.order_id)

                # Order ID should follow expected format
                assert response.order_id.startswith("TEST-")
                assert len(response.order_id) == 11  # TEST-XXXXXX

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("1"), max_value=Decimal("500"), places=0),
        limit_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
        market_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
    )
    def test_limit_order_execution_invariant(self, symbol: str, quantity: Decimal, limit_price: Decimal, market_price: Decimal) -> None:
        """Test that limit orders execute only at favorable prices."""
        assume(quantity <= 500)  # Stay well within position limits

        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol to market
        broker.market_sim.add_symbol(symbol, market_price)

        # Place buy limit order
        buy_request = orders_pb2.PlaceOrderRequest(
            symbol=symbol,
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=float(quantity),
            limit_price=float(limit_price),
        )
        buy_response = broker.PlaceOrder(buy_request, None)
        assert buy_response.accepted

        order = broker.orders[buy_response.order_id]

        # Check execution logic
        market = broker.market_sim.markets[symbol]
        if limit_price >= market.ask:
            # Should execute immediately at market ask
            assert order.status == common_pb2.ORDER_STATUS_FILLED
        else:
            # Should remain open (or might execute with 30% probability)
            assert order.status in [common_pb2.ORDER_STATUS_SUBMITTED, common_pb2.ORDER_STATUS_FILLED]

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        buy_quantities=st.lists(st.decimals(min_value=Decimal("1"), max_value=Decimal("100"), places=0), min_size=2, max_size=5),
        prices=st.lists(st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2), min_size=2, max_size=5),
    )
    def test_average_price_calculation(self, symbol: str, buy_quantities: list, prices: list) -> None:
        """Test that average position price is calculated correctly."""
        assume(len(buy_quantities) == len(prices))

        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol to market
        broker.market_sim.add_symbol(symbol, prices[0])

        total_cost = Decimal("0")
        total_quantity = Decimal("0")

        # Place multiple buy orders at different prices
        for qty, price in zip(buy_quantities, prices):
            # Update market price
            broker.market_sim.markets[symbol].last_price = price
            broker.market_sim.markets[symbol].bid = price - Decimal("0.01")
            broker.market_sim.markets[symbol].ask = price + Decimal("0.01")

            request = orders_pb2.PlaceOrderRequest(
                symbol=symbol,
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=float(qty),
            )
            response = broker.PlaceOrder(request, None)

            if response.accepted:
                # Track for manual calculation
                # Market orders execute at ask
                exec_price = price + Decimal("0.01")
                total_cost += qty * exec_price
                total_quantity += qty

                # Check average price
                if total_quantity > 0:
                    expected_avg = total_cost / total_quantity
                    actual_avg = Decimal(str(broker.positions[symbol].avg_price))

                    # Allow for small rounding differences
                    assert abs(actual_avg - expected_avg) < Decimal("0.01")

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("1"), max_value=Decimal("100"), places=0),
        buy_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("100"), places=2),
        sell_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
    )
    def test_realized_pnl_calculation(self, symbol: str, quantity: Decimal, buy_price: Decimal, sell_price: Decimal) -> None:
        """Test that realized P&L is calculated correctly."""
        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol to market at buy price
        broker.market_sim.add_symbol(symbol, buy_price)

        # Buy position
        buy_request = orders_pb2.PlaceOrderRequest(
            symbol=symbol,
            side=common_pb2.ORDER_SIDE_BUY,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=float(quantity),
        )
        buy_response = broker.PlaceOrder(buy_request, None)
        assert buy_response.accepted

        # Record buy execution price (at ask)
        buy_exec_price = buy_price + Decimal("0.01")

        # Update market to sell price
        broker.market_sim.markets[symbol].last_price = sell_price
        broker.market_sim.markets[symbol].bid = sell_price - Decimal("0.01")
        broker.market_sim.markets[symbol].ask = sell_price + Decimal("0.01")

        # Sell entire position
        sell_request = orders_pb2.PlaceOrderRequest(
            symbol=symbol,
            side=common_pb2.ORDER_SIDE_SELL,
            order_type=common_pb2.ORDER_TYPE_MARKET,
            quantity=float(quantity),
        )
        sell_response = broker.PlaceOrder(sell_request, None)
        assert sell_response.accepted

        # Record sell execution price (at bid)
        sell_exec_price = sell_price - Decimal("0.01")

        # Calculate expected P&L
        expected_pnl = quantity * (sell_exec_price - buy_exec_price)
        actual_pnl = Decimal(str(broker.positions[symbol].realized_pnl))

        # Allow for small rounding differences due to float conversions
        # Use relative tolerance based on trade size
        trade_value = quantity * max(buy_price, sell_price)
        tolerance = max(Decimal("0.01"), trade_value * Decimal("0.001"))
        assert abs(actual_pnl - expected_pnl) <= tolerance

    @given(
        initial_cash=st.decimals(min_value=Decimal("10000"), max_value=Decimal("1000000"), places=2),
        trades=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=5).filter(lambda x: x.strip() and x.isalnum()),
                st.sampled_from([common_pb2.ORDER_SIDE_BUY, common_pb2.ORDER_SIDE_SELL]),
                st.decimals(min_value=Decimal("1"), max_value=Decimal("100"), places=0),
                st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
            ),
            min_size=1,
            max_size=10,
        ),
    )
    def test_portfolio_value_consistency(self, initial_cash: Decimal, trades: list) -> None:
        """Test that portfolio value = cash + sum(position values)."""
        broker = RealisticMockBroker(initial_cash=initial_cash)
        broker.enable_rejections = False

        # Initialize all symbols
        for symbol, _, _, price in trades:
            if symbol not in broker.market_sim.markets:
                broker.market_sim.add_symbol(symbol, price)

        # Execute trades
        for symbol, side, quantity, price in trades:
            # Update market price
            broker.market_sim.markets[symbol].last_price = price
            broker.market_sim.markets[symbol].bid = price - Decimal("0.01")
            broker.market_sim.markets[symbol].ask = price + Decimal("0.01")

            request = orders_pb2.PlaceOrderRequest(
                symbol=symbol,
                side=side,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=float(quantity),
            )
            response = broker.PlaceOrder(request, None)

            if response.accepted:
                # Verify portfolio value consistency
                cash = Decimal(str(broker.account.cash_balance))
                position_values = Decimal("0")

                for _, position in broker.positions.items():
                    if position.quantity != 0:
                        position_values += Decimal(str(position.market_value))

                expected_portfolio = cash + position_values
                actual_portfolio = Decimal(str(broker.account.portfolio_value))

                # Allow for small rounding differences
                assert abs(actual_portfolio - expected_portfolio) < Decimal("0.01")
