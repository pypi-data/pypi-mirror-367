"""Serve command implementation for running strategy as gRPC server."""

import os
from typing import Any

from ..utils.colors import Colors, print_colored, print_header
from ..utils.loader import load_strategy_class


def cmd_serve(args: Any) -> int:
    """Run strategy as gRPC server."""
    module_path = args.module
    class_name = args.class_name

    if not os.path.exists(module_path):
        print_colored(f"Error: {module_path} not found", Colors.FAIL)
        return 1

    print_header(f"Starting gRPC server for {class_name}")

    try:
        # Load strategy class
        strategy_class = load_strategy_class(module_path, class_name)

        # Import serve function
        from tektii.strategy.grpc.service import serve

        # Start server
        print_colored(f"Starting server on port {args.port}...", Colors.OKCYAN)
        if args.broker:
            print_colored(f"Connecting to broker at {args.broker}", Colors.OKCYAN)
        serve(
            strategy_class=strategy_class,
            port=args.port,
            broker_address=args.broker,
        )
    except Exception as e:
        print_colored(f"Error: {e}", Colors.FAIL)
        import traceback

        traceback.print_exc()
        return 1

    return 0
