"""Tektii SDK - Build trading strategies that run anywhere.

The Tektii SDK provides a provider-agnostic framework for building algorithmic
trading strategies that communicate via gRPC with external trading systems.

Example:
    ```python
    from tektii import TektiiStrategy
    from tektii.strategy.grpc import market_data_pb2

    class MyStrategy(TektiiStrategy):
        def on_market_data(self, tick_data=None, bar_data=None):
            if tick_data and tick_data.last > 100:
                # Use self._broker_stub to place orders
                pass
    ```
"""

__version__ = "0.1.0"
__author__ = "Tektii"
__email__ = "support@tektii.com"

from tektii.strategy import TektiiStrategy, serve

# Proto types are imported directly from grpc modules when needed

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__email__",
    # Core strategy class
    "TektiiStrategy",
    # Server
    "serve",
]
