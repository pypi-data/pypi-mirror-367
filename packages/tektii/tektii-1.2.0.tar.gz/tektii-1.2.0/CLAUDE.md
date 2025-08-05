# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Setup & Development
```bash
# First-time setup
make setup          # Complete setup with virtual environment, dependencies, and proto generation

# Generate proto files (if proto definitions change)
make proto          # Pull latest proto files and generate Python code

# Install dependencies
make install        # Install package
make install-dev    # Install with development dependencies
```

### Quality Checks (ALWAYS run before completing tasks)
```bash
# Run ALL quality checks
make check          # Runs lint, type-check, and test

# Individual checks
make lint           # Run flake8 and bandit security checks
make type-check     # Run mypy type checking
make test           # Run all tests with coverage
make format         # Auto-format with black and isort
```

### Testing Commands
```bash
# Test execution
make test           # Run all tests with coverage
make test-unit      # Run unit tests only
make test-fast      # Run fast unit tests (skip slow tests)

# Run specific test
pytest tests/unit/models/test_orders.py::TestOrderBuilder::test_fluent_api -xvs
```

## High-Level Architecture

The **tektii** is a Python SDK for building algorithmic trading strategies that run on the Tektii platform.

### Core Components

**Strategy Base (`tektii/strategy/base.py`)**
- `TektiiStrategy` abstract base class that all strategies inherit from
- Event-driven architecture with methods like `on_market_data()`, `on_order_update()`, etc.
- Manages order lifecycle, position tracking, and account state

**Models (`tektii/strategy/models/`)**
- Type-safe Pydantic models for all trading entities
- `orders.py`: Order models with fluent `OrderBuilder` API
- `events.py`: Event models for market data, order updates, position changes
- `enums.py`: Trading enumerations (OrderType, OrderSide, OrderStatus, etc.)
- `conversions.py`: Proto ↔ Python model conversions

**gRPC Service (`tektii/strategy/grpc/`)**
- Implements gRPC server for strategy execution
- Handles bi-directional communication with Tektii Engine
- Auto-generated proto files for type-safe messaging

**CLI (`tektii/cli.py` & `tektii/commands/`)**
- `tektii new`: Create new strategy from template
- `tektii serve`: Run strategy as gRPC service
- `tektii test`: Test strategy functionality
- `tektii validate`: Validate strategy code
- `tektii push`: Deploy to Tektii platform

**Testing Framework (`tektii/testing/`)**
- `StrategyTestHarness`: Test harness for strategy development
- `MockBrokerService`: Simulated broker for testing

### Key Design Patterns

1. **Event-Driven Architecture**: Strategies respond to market events asynchronously
2. **Type Safety**: Comprehensive Pydantic models with validation
3. **Financial Precision**: All monetary values use Python's `Decimal` type
4. **Builder Pattern**: Fluent API for order construction
5. **Proto Integration**: gRPC for cross-language communication

### Development Workflow

1. Create strategy by inheriting from `TektiiStrategy`
2. Implement event handlers (`on_market_data`, `on_order_update`, etc.)
3. Use `OrderBuilder` to create orders with validation
4. Test with `StrategyTestHarness` and mock data
5. Deploy with `tektii push` command

### Important Implementation Notes

- **Decimal Precision**: Always use `Decimal` for prices/quantities (6 decimal places)
- **Proto Conversions**: Field names may differ between Python models and proto (use conversion utilities)
- **Order Validation**: Orders are validated both client-side and server-side
- **State Management**: Strategy state persists across event callbacks
- **Error Handling**: Use domain-specific exceptions from `models/errors.py`
