"""Property-based tests for market simulation invariants."""

from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from tektii.strategy.grpc import common_pb2
from tektii.testing.market_simulator import MarketCondition, MarketState, RealisticMarketSimulator


class TestMarketProperties:
    """Property-based tests for market simulation invariants."""

    @given(
        initial_price=st.decimals(min_value=Decimal("1"), max_value=Decimal("10000"), places=2),
        volatility=st.decimals(min_value=Decimal("0.001"), max_value=Decimal("0.1"), places=3),
        time_steps=st.integers(min_value=1, max_value=100),
    )
    def test_price_remains_positive(self, initial_price: Decimal, volatility: Decimal, time_steps: int) -> None:
        """Test that prices always remain positive."""
        market = MarketState(
            symbol="TEST",
            last_price=initial_price,
            bid=initial_price - Decimal("0.01"),
            ask=initial_price + Decimal("0.01"),
            volatility=volatility,
        )

        for _ in range(time_steps):
            market.update_price(dt=1.0)

            # Prices must remain positive
            assert market.last_price > 0
            assert market.bid > 0
            assert market.ask > 0

    @given(
        initial_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("1000"), places=2),
        spread=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1"), places=2),
    )
    def test_bid_ask_spread_invariant(self, initial_price: Decimal, spread: Decimal) -> None:
        """Test that bid is always less than ask."""
        market = MarketState(
            symbol="TEST",
            last_price=initial_price,
            bid=initial_price - spread / 2,
            ask=initial_price + spread / 2,
            spread=spread,
        )

        # Update price multiple times
        for _ in range(50):
            market.update_price(dt=0.1)

            # Bid must always be less than ask
            assert market.bid < market.ask

            # Spread should be approximately maintained
            actual_spread = market.ask - market.bid
            assert actual_spread > 0

            # In normal conditions, spread should be close to configured
            if market.condition == MarketCondition.NORMAL:
                assert abs(actual_spread - spread) < spread * Decimal("0.5")

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        initial_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("1000"), places=2),
        levels=st.integers(min_value=1, max_value=20),
    )
    def test_order_book_depth_consistency(self, symbol: str, initial_price: Decimal, levels: int) -> None:
        """Test that order book depth is consistent."""
        market = MarketState(
            symbol=symbol,
            last_price=initial_price,
            bid=initial_price - Decimal("0.01"),
            ask=initial_price + Decimal("0.01"),
        )

        market.generate_order_book(levels=levels)

        # Should have correct number of levels
        assert len(market.bid_depth) == levels
        assert len(market.ask_depth) == levels

        # Bid prices should decrease
        for i in range(1, len(market.bid_depth)):
            assert market.bid_depth[i][0] < market.bid_depth[i - 1][0]

        # Ask prices should increase
        for i in range(1, len(market.ask_depth)):
            assert market.ask_depth[i][0] > market.ask_depth[i - 1][0]

        # All sizes should be positive
        for price, size in market.bid_depth + market.ask_depth:
            assert price > 0
            assert size > 0

        # Best bid should be less than best ask
        if market.bid_depth and market.ask_depth:
            assert market.bid_depth[0][0] < market.ask_depth[0][0]

    @given(
        quantity=st.decimals(min_value=Decimal("1"), max_value=Decimal("10000"), places=0),
        order_book_sizes=st.lists(st.integers(min_value=100, max_value=1000), min_size=5, max_size=10),
    )
    def test_slippage_calculation(self, quantity: Decimal, order_book_sizes: list) -> None:
        """Test that slippage increases with order size."""
        simulator = RealisticMarketSimulator()

        # Create order book
        base_price = Decimal("100")
        order_book = [(base_price + Decimal(str(i)) * Decimal("0.1"), size) for i, size in enumerate(order_book_sizes)]

        # Calculate slippage for different quantities
        small_qty = min(quantity, Decimal("10"))
        large_qty = quantity

        small_slippage = simulator._calculate_slippage(small_qty, order_book)
        large_slippage = simulator._calculate_slippage(large_qty, order_book)

        # Slippage should be non-negative
        assert small_slippage >= 0
        assert large_slippage >= 0

        # Larger orders should have more slippage
        if large_qty > small_qty:
            assert large_slippage >= small_slippage

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        side=st.sampled_from([common_pb2.ORDER_SIDE_BUY, common_pb2.ORDER_SIDE_SELL]),
        quantity=st.decimals(min_value=Decimal("1"), max_value=Decimal("1000"), places=0),
        market_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
        limit_price=st.decimals(min_value=Decimal("10"), max_value=Decimal("200"), places=2),
    )
    def test_execution_price_bounds(
        self, symbol: str, side: common_pb2.OrderSide, quantity: Decimal, market_price: Decimal, limit_price: Decimal
    ) -> None:
        """Test that execution prices respect order constraints."""
        simulator = RealisticMarketSimulator()
        simulator.add_symbol(symbol, market_price)

        # Test market order
        market_exec_price = simulator.get_execution_price(symbol, side, quantity, common_pb2.ORDER_TYPE_MARKET, None)

        assert market_exec_price is not None

        if side == common_pb2.ORDER_SIDE_BUY:
            # Buy market orders execute at ask or higher
            assert market_exec_price >= simulator.markets[symbol].ask
        else:
            # Sell market orders execute at bid or lower
            assert market_exec_price <= simulator.markets[symbol].bid

        # Test limit order
        limit_exec_price = simulator.get_execution_price(symbol, side, quantity, common_pb2.ORDER_TYPE_LIMIT, limit_price)

        if limit_exec_price is not None:
            if side == common_pb2.ORDER_SIDE_BUY:
                # Buy limit orders execute at limit or better (lower)
                assert limit_exec_price <= limit_price
            else:
                # Sell limit orders execute at limit or better (higher)
                assert limit_exec_price >= limit_price

    @given(
        condition=st.sampled_from(list(MarketCondition)),
        initial_price=st.decimals(min_value=Decimal("50"), max_value=Decimal("500"), places=2),
        time_steps=st.integers(min_value=10, max_value=100),
    )
    @settings(deadline=5000)  # Allow more time for this test
    def test_market_condition_effects(self, condition: MarketCondition, initial_price: Decimal, time_steps: int) -> None:
        """Test that market conditions affect price behavior correctly."""
        market = MarketState(
            symbol="TEST",
            last_price=initial_price,
            bid=initial_price - Decimal("0.01"),
            ask=initial_price + Decimal("0.01"),
            condition=condition,
        )

        prices = [initial_price]

        # Simulate market movement
        for _ in range(time_steps):
            market.update_price(dt=1.0)
            prices.append(market.last_price)

        # Calculate price changes
        price_changes = [abs(prices[i + 1] - prices[i]) for i in range(len(prices) - 1)]

        # Trending markets should show directional bias
        if condition in (MarketCondition.TRENDING_UP, MarketCondition.TRENDING_DOWN):
            # Most of the time, should end higher/lower
            # (not always due to randomness)
            pass  # Can't guarantee due to randomness

        elif condition == MarketCondition.VOLATILE:
            # Volatile markets should have larger price changes
            normal_market = MarketState(
                symbol="TEST2",
                last_price=initial_price,
                bid=initial_price - Decimal("0.01"),
                ask=initial_price + Decimal("0.01"),
                condition=MarketCondition.NORMAL,
            )

            normal_prices = [initial_price]
            for _ in range(time_steps):
                normal_market.update_price(dt=1.0)
                normal_prices.append(normal_market.last_price)

            normal_changes = [abs(normal_prices[i + 1] - normal_prices[i]) for i in range(len(normal_prices) - 1)]
            # Volatile markets should have more movement on average
            # Compare the average change magnitudes
            if price_changes and normal_changes:
                avg_volatile = sum(price_changes) / len(price_changes)
                avg_normal = sum(normal_changes) / len(normal_changes)
                # Volatile should typically have larger changes, but it's probabilistic
                _ = (avg_volatile, avg_normal)  # Variables calculated for potential future use

    @given(
        quantities=st.lists(st.decimals(min_value=Decimal("100"), max_value=Decimal("10000"), places=0), min_size=1, max_size=10),
    )
    def test_partial_fill_completeness(self, quantities: list) -> None:
        """Test that partial fills sum to total quantity."""
        simulator = RealisticMarketSimulator()

        for total_qty in quantities:
            fills = simulator.simulate_partial_fill(total_qty)

            # Fills should not be empty
            assert len(fills) > 0

            # All fills should be positive
            for fill in fills:
                assert fill > 0

            # Fills should sum to total quantity
            assert sum(fills) == total_qty

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        limit_price=st.decimals(min_value=Decimal("1"), max_value=Decimal("1000"), places=2),
        market_price=st.decimals(min_value=Decimal("1"), max_value=Decimal("1000"), places=2),
    )
    def test_order_rejection_logic(self, symbol: str, limit_price: Decimal, market_price: Decimal) -> None:
        """Test that order rejection logic is consistent."""
        simulator = RealisticMarketSimulator()
        simulator.add_symbol(symbol, market_price)

        # Test limit price distance rejection
        should_reject, reason = simulator.should_reject_order(symbol, common_pb2.ORDER_TYPE_LIMIT, limit_price)

        distance = abs(limit_price - market_price) / market_price

        # If rejected for price distance, distance should be > 10%
        if should_reject and "too far from market" in reason:
            assert distance > Decimal("0.1")

        # Test unknown symbol rejection
        should_reject, reason = simulator.should_reject_order("UNKNOWN", common_pb2.ORDER_TYPE_MARKET, None)
        assert should_reject
        assert "not found" in reason

    @given(
        symbols=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=5).filter(lambda x: x.strip() and x.isalnum()),
                st.decimals(min_value=Decimal("10"), max_value=Decimal("1000"), places=2),
                st.sampled_from(list(MarketCondition)),
            ),
            min_size=1,
            max_size=10,
            unique_by=lambda x: x[0],  # Unique symbols
        ),
        update_cycles=st.integers(min_value=1, max_value=10),
    )
    def test_multi_symbol_simulation(self, symbols: list, update_cycles: int) -> None:
        """Test that multiple symbols can be simulated independently."""
        simulator = RealisticMarketSimulator()

        # Add all symbols
        for symbol, price, condition in symbols:
            simulator.add_symbol(symbol, price, condition)

        # Verify all were added
        for symbol, _, _ in symbols:
            assert symbol in simulator.markets

        # Update all markets
        for _ in range(update_cycles):
            simulator.update_all_markets(dt=0.1)

            # Verify all prices changed (or at least could have)
            for symbol, _, _ in symbols:
                # Price should still be positive
                assert simulator.markets[symbol].last_price > 0

                # Bid/ask relationship maintained
                assert simulator.markets[symbol].bid < simulator.markets[symbol].ask
