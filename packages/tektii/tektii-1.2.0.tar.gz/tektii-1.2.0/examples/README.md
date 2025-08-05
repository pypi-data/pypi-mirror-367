# Tektii SDK Examples

This directory contains example strategies demonstrating how to use the Tektii SDK.

## Examples

### 01. Hello World Strategy

Basic introduction to the Tektii SDK - `01_hello_world.py`

### 02. Event Handling Demo

Demonstrates all event handling capabilities - `02_event_handling.py`
- Market data handling (ticks and bars)
- Order update events
- Position update events
- Account update events
- Trade execution events
- System events

### 03. Order Interactions Demo

Demonstrates all order service interactions - `03_order_interactions.py`
- Order validation before submission
- Placing various order types (market, limit, stop)
- Canceling pending orders
- Closing positions (full and partial)
- Using protective orders (stop loss + take profit)

### Model Usage Demo

Shows how to use various models in the SDK - `model_usage_demo.py`
- OrderBuilder fluent API
- Market data models
- Order and position models
- Risk models
- Option Greeks

## Hello World Strategy

The `hello_world_strategy.py` file demonstrates the basic structure of a Tektii strategy:

- Inheriting from `TektiiStrategy` base class
- Implementing the required `on_market_data()` method
- Handling tick and bar data
- Optional event handlers like `on_order_update()`
- Lifecycle methods like `on_initialize()` and `on_shutdown()`

### Running the Example

1. **Direct execution** (for testing):
   ```bash
   python hello_world_strategy.py
   ```

2. **Validate the strategy**:
   ```bash
   tektii validate hello_world_strategy.py
   ```

3. **Run as a gRPC service**:
   ```bash
   tektii run hello_world_strategy.py
   ```

## Key Concepts

### Market Data Handling

Strategies receive market data through the `on_market_data()` method:

```python
def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None):
    if tick_data:
        # Handle tick data (bid/ask/last prices)
        pass
    elif bar_data:
        # Handle bar data (OHLCV)
        pass
```

### Order Management

For actual trading strategies, you would use the broker stub to place orders:

```python
# Note: Order placement requires connection to Tektii Engine
# This is typically done via self._broker_stub when available
```

### Event Handlers

Strategies can optionally implement these event handlers:

- `on_order_update()`: Track order status changes
- `on_position_update()`: Monitor position changes
- `on_account_update()`: Handle account balance updates
- `on_trade()`: React to trade executions
- `on_system_event()`: Handle system notifications

## Next Steps

- Review the models in `tektii/strategy/models/` for available data structures
- Check the base class in `tektii/strategy/base.py` for all available methods
- Use the `tektii` CLI to validate and test your strategies
