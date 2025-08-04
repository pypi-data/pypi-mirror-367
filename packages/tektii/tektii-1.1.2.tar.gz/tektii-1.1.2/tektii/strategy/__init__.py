"""Tektii Strategy SDK - Build trading strategies that run anywhere.

This SDK provides a provider-agnostic framework for building algorithmic trading
strategies that communicate via gRPC with external trading systems.
"""

from tektii.strategy.base import TektiiStrategy
from tektii.strategy.grpc.service import serve

__all__ = [
    # Base strategy class
    "TektiiStrategy",
    # Order helpers
    "create_order_request",
    "validate_order_request",
    "market_buy_request",
    "market_sell_request",
    "limit_buy_request",
    "limit_sell_request",
    "stop_loss_request",
    "take_profit_request",
    # Server
    "serve",
]

__version__ = "0.1.0"
