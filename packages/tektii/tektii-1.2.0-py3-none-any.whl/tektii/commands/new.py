"""New command implementation for creating strategy templates."""

import os
from typing import Any


def cmd_new(args: Any) -> int:
    """Create a new strategy from template."""
    strategy_name = args.name
    force = args.force

    # Convert strategy name to PascalCase for class name
    class_name = "".join(word.capitalize() for word in strategy_name.replace("-", "_").split("_"))
    if not class_name.endswith("Strategy"):
        class_name += "Strategy"

    # Create file name
    strategy_file = f"{strategy_name}.py"

    # Check if file already exists
    if os.path.exists(strategy_file) and not force:
        print(f"Error: {strategy_file} already exists. Use --force to overwrite.")
        return 1

    # Create strategy content
    strategy_content = _get_template(class_name)

    # Write strategy file
    with open(strategy_file, "w") as f:
        f.write(strategy_content)

    print(f"✓ Created {strategy_file}")

    # Print next steps
    print("\nNext steps:")
    print(f"1. Edit {strategy_file} to implement your trading logic")
    print(f"2. Test locally: python {strategy_file}")
    print(f"3. Validate: tektii validate {strategy_file}")
    print(f"4. Deploy: tektii push {strategy_file} {class_name}")

    return 0


def _get_template(class_name: str) -> str:
    """Get the strategy template."""
    return f'''"""
{class_name} - A simple trading strategy.

This strategy demonstrates the basic structure of a Tektii strategy.
Modify this template to implement your trading logic.
"""

from decimal import Decimal
from typing import Optional

from tektii.strategy import TektiiStrategy
from tektii.strategy.models import BarData, OrderUpdateEvent, TickData


class {class_name}(TektiiStrategy):
    """A simple trading strategy."""

    def __init__(self) -> None:
        """Initialize the strategy."""
        super().__init__()
        self.tick_count = 0
        self.bar_count = 0

    def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None) -> None:
        """Handle incoming market data.

        Either tick_data or bar_data will be provided, not both.
        """
        if tick_data:
            self.tick_count += 1
            # Add your tick data logic here
            pass

        elif bar_data:
            self.bar_count += 1
            # Add your bar data logic here
            pass

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order update events."""
        # Add your order update logic here
        pass

    def on_initialize(self, config: dict[str, str], symbols: list[str]) -> None:
        """Initialize the strategy with configuration."""
        print(f"{{{class_name}}} initialized with symbols: {{symbols}}")

    def on_shutdown(self) -> None:
        """Clean up on strategy shutdown."""
        print(f"{{{class_name}}} shutting down. Processed {{self.tick_count}} ticks and {{self.bar_count}} bars")


if __name__ == "__main__":
    # Test the strategy locally
    strategy = {class_name}()
    print(f"Created {{strategy.__class__.__name__}} successfully!")
'''
