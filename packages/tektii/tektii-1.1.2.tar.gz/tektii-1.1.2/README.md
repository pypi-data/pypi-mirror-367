# Tektii Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/tektii)](https://pypi.org/project/tektii/)
[![Python Version](https://img.shields.io/pypi/pyversions/tektii)](https://pypi.org/project/tektii/)
[![License](https://img.shields.io/pypi/l/tektii)](https://github.com/tektii/tektii-sdk-python/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://docs.tektii.com/sdk)
[![CI Status](https://img.shields.io/github/actions/workflow/status/tektii/tektii-sdk-python/ci.yml?branch=main)](https://github.com/tektii/tektii-sdk-python/actions)
[![Coverage](https://img.shields.io/codecov/c/github/tektii/tektii-sdk-python)](https://codecov.io/gh/tektii/tektii-sdk-python)

**Build trading strategies that run anywhere - Write Once. Trade Everywhere.**

The Tektii Python SDK provides a powerful, type-safe framework for building algorithmic trading strategies. Whether you're backtesting historical data or deploying to production, Tektii's event-driven architecture and comprehensive tooling help you focus on strategy development.

## 🚀 Features

- **Event-Driven Architecture** - React to market data and order updates in real-time
- **Type-Safe Models** - Pydantic-powered models with full type hints and validation
- **Financial Precision** - Built-in Decimal support for accurate financial calculations
- **Fluent API** - Intuitive order builder with compile-time safety
- **Testing Framework** - Comprehensive test harness for strategy development
- **gRPC Integration** - High-performance communication with the Tektii Engine
- **Production Ready** - Deploy directly to Tektii's cloud infrastructure

## 📦 Installation

### Requirements

- Python 3.11 or higher
- pip or poetry

### Install from PyPI

```bash
pip install tektii
```

### Install for Development

```bash
# Clone the repository
git clone https://github.com/tektii/tektii-sdk-python.git
cd tektii-sdk-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
make setup  # or: pip install -e ".[dev]"
```

## 🎯 Quick Start

### 1. Create Your First Strategy

```python
from decimal import Decimal
from typing import Optional

from tektii.strategy import TektiiStrategy
from tektii.strategy.models import BarData, OrderSide, OrderType, TickData


class MyStrategy(TektiiStrategy):
    """A simple moving average crossover strategy."""

    def __init__(self):
        super().__init__()
        self.position_size = Decimal("100")

    def on_market_data(
        self,
        tick_data: Optional[TickData] = None,
        bar_data: Optional[BarData] = None
    ) -> None:
        """React to incoming market data."""
        if bar_data and bar_data.close > Decimal("150.00"):
            # Create and submit a buy order
            order = (
                self.create_order()
                .symbol(bar_data.symbol)
                .side(OrderSide.BUY)
                .quantity(self.position_size)
                .order_type(OrderType.MARKET)
                .build()
            )
            self.submit_order(order)
```

### 2. Test Your Strategy

```python
from tektii.testing import StrategyTestHarness
from tektii.testing.fixtures import create_bar_data


def test_my_strategy():
    # Create test harness
    harness = StrategyTestHarness(MyStrategy)

    # Send test market data
    test_bar = create_bar_data(
        symbol="AAPL",
        close=Decimal("151.00")  # Above our threshold
    )
    harness.process_bar_data(test_bar)

    # Verify order was created
    orders = harness.get_orders()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.BUY
```

### 3. Run Your Strategy

```bash
# Create a new strategy from template
tektii new my-strategy

# Test your strategy
tektii test

# Run strategy locally
tektii serve --port 50051

# Deploy to Tektii Cloud
tektii push
```

## 📚 Documentation

### Strategy Development

Your strategy should inherit from `TektiiStrategy` and implement the event handlers:

```python
class TektiiStrategy:
    def on_initialize(self, config: dict[str, str], symbols: list[str]) -> None:
        """Initialize strategy with configuration."""

    def on_market_data(self, tick_data: Optional[TickData], bar_data: Optional[BarData]) -> None:
        """Handle incoming market data."""

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order status updates."""

    def on_position_update(self, position_update: PositionUpdateEvent) -> None:
        """Handle position changes."""

    def on_account_update(self, account_update: AccountUpdateEvent) -> None:
        """Handle account updates."""

    def on_shutdown(self) -> None:
        """Clean up resources."""
```

### Order Management

Use the fluent order builder API for type-safe order creation:

```python
# Market order
market_order = (
    self.create_order()
    .symbol("AAPL")
    .side(OrderSide.BUY)
    .quantity(Decimal("100"))
    .order_type(OrderType.MARKET)
    .build()
)

# Limit order with time-in-force
limit_order = (
    self.create_order()
    .symbol("GOOGL")
    .side(OrderSide.SELL)
    .quantity(Decimal("50"))
    .order_type(OrderType.LIMIT)
    .limit_price(Decimal("2500.00"))
    .time_in_force(TimeInForce.GTC)
    .build()
)

# Stop-loss order
stop_order = (
    self.create_order()
    .symbol("MSFT")
    .side(OrderSide.SELL)
    .quantity(Decimal("200"))
    .order_type(OrderType.STOP)
    .stop_price(Decimal("380.00"))
    .build()
)
```

### Error Handling

The SDK provides specific exceptions for different error scenarios:

```python
from tektii.strategy.models.errors import (
    InvalidOrderError,
    ValidationError,
    BrokerConnectionError,
)

try:
    order = self.create_order().build()  # Missing required fields
except ValidationError as e:
    self.log_error(f"Order validation failed: {e}")
except BrokerConnectionError as e:
    self.log_error(f"Broker connection lost: {e}")
```

## 🧪 Testing

The SDK includes comprehensive testing utilities:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/models/test_orders.py

# Run with coverage
make test-coverage

# Run only fast tests
make test-fast
```

### Writing Tests

```python
import pytest
from decimal import Decimal
from tektii.testing import StrategyTestHarness


class TestMyStrategy:
    def test_strategy_initialization(self):
        harness = StrategyTestHarness(MyStrategy)
        assert harness.strategy is not None

    def test_order_creation_on_signal(self):
        harness = StrategyTestHarness(MyStrategy)

        # Simulate market conditions
        harness.process_bar_data(
            create_bar_data(symbol="AAPL", close=Decimal("155.00"))
        )

        # Verify strategy behavior
        assert len(harness.get_orders()) == 1
        assert harness.get_portfolio_value() > Decimal("0")
```

## 🔧 CLI Commands

The Tektii CLI provides commands for the complete development lifecycle:

| Command | Description |
|---------|-------------|
| `tektii new <name>` | Create a new strategy from template |
| `tektii serve` | Run strategy as gRPC service |
| `tektii test` | Run strategy tests |
| `tektii validate` | Validate strategy code |
| `tektii push` | Deploy to Tektii platform |
| `tektii logs` | View strategy logs |
| `tektii status` | Check deployment status |

## 🏗️ Project Structure

```
my-strategy/
├── strategy.py          # Your strategy implementation
├── requirements.txt     # Dependencies
├── config.yaml         # Strategy configuration
├── tests/
│   ├── test_strategy.py
│   └── fixtures.py
├── Dockerfile          # Container configuration
└── README.md          # Strategy documentation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
make install-dev

# Run linting and formatting
make lint
make format

# Run type checking
make type-check

# Run all checks before committing
make check
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Documentation](https://docs.tektii.com/sdk)
- [API Reference](https://docs.tektii.com/sdk/api)
- [Examples](https://github.com/tektii/tektii-sdk-python/tree/main/examples)
- [Changelog](CHANGELOG.md)
- [Roadmap](https://github.com/tektii/tektii-sdk-python/projects/1)

## 💬 Support

- [GitHub Issues](https://github.com/tektii/tektii-sdk-python/issues)
- [Discord Community](https://discord.gg/tektii)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/tektii)
- Email: support@tektii.com

## 🙏 Acknowledgments

Built with ❤️ by the Tektii team. Special thanks to all our contributors and the open-source community.

---

**Ready to build your trading strategy?** [Get started with our tutorials →](https://docs.tektii.com/sdk/quickstart)
