"""gRPC service implementation for Tektii Strategy SDK.

This module implements the gRPC server that receives events from external
trading systems and routes them to user strategies.
"""

from __future__ import annotations

import logging
import signal
import sys
import threading
import time
from concurrent import futures
from typing import Any, Optional, Type

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from tektii.strategy.base import TektiiStrategy
from tektii.strategy.grpc import orders_pb2
from tektii.strategy.grpc import service_pb2_grpc as pb2_grpc
from tektii.strategy.grpc.connection_manager import BrokerConnectionManager
from tektii.strategy.grpc.service_pb2_grpc import TektiiBrokerStub

logger = logging.getLogger(__name__)


class TektiiStrategyService(pb2_grpc.TektiiStrategyServicer):
    """gRPC service implementation for Tektii strategies.

    This service receives events from external trading systems and
    routes them to the strategy. The strategy communicates with the
    broker via a separate gRPC channel for order management and queries.
    """

    def __init__(self, strategy: TektiiStrategy, broker_address: Optional[str] = None):
        """Initialize the service with a strategy instance.

        Args:
            strategy: The strategy instance to handle events
            broker_address: Optional broker service address (e.g., "localhost:50052")
        """
        self.strategy = strategy
        self._shutdown_event = threading.Event()
        self._broker_address = broker_address
        self._connection_manager: Optional[BrokerConnectionManager] = None
        self._broker_stub_lock = threading.Lock()
        self._initialized = False

        # Note: Connection manager will be created during Initialize call
        # to ensure proper startup sequencing

    def ProcessEvent(self, request: orders_pb2.TektiiEvent, context: grpc.ServicerContext) -> orders_pb2.ProcessEventResponse:
        """Process an incoming event.

        The strategy handles the event and may make calls to the broker
        to manage orders. This method returns a simple acknowledgment.

        Args:
            request: The event to process
            context: gRPC context

        Returns:
            ProcessEventResponse with success/error status
        """
        try:
            logger.debug(f"Processing event: {request.event_id}")

            # Route the event to the strategy
            self.strategy._handle_event(request)

            # Return success response
            response = orders_pb2.ProcessEventResponse(success=True)

            # Add metadata for debugging
            response.metadata["event_id"] = request.event_id
            response.metadata["processed_at"] = str(int(time.time() * 1_000_000))

            return response

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error processing event: {str(e)}")
            return orders_pb2.ProcessEventResponse(success=False, error=str(e))

    def Initialize(self, request: orders_pb2.InitRequest, context: grpc.ServicerContext) -> orders_pb2.InitResponse:
        """Initialize the strategy.

        Args:
            request: Initialization request with config and symbols
            context: gRPC context

        Returns:
            InitResponse indicating success or failure
        """
        try:
            logger.info(f"Initializing strategy: {request.strategy_id}")

            # Check if broker connection is required and available
            # Check if already initialized
            if self._initialized:
                logger.warning("Strategy already initialized")
                return orders_pb2.InitResponse(
                    success=False,
                    message="Strategy already initialized",
                )

            broker_status = "not configured"

            if self._broker_address:
                logger.info(f"Creating connection to broker at {self._broker_address}")

                # Create connection manager now during Initialize
                self._connection_manager = BrokerConnectionManager(
                    broker_address=self._broker_address,
                    on_connected=self._on_broker_connected,
                    on_disconnected=self._on_broker_disconnected,
                    health_check_interval=5.0,
                    reconnect_interval=2.0,
                )

                # Start connection manager and wait for broker to be healthy
                logger.info("Waiting for broker to become healthy...")
                if self._connection_manager.start():
                    # Wait up to 60 seconds for connection to be established
                    logger.info("Waiting for connection to stabilize...")
                    if self._connection_manager.wait_for_connection(timeout=60.0):
                        broker_status = "connected"
                        logger.info("Broker connection established and verified healthy")
                    else:
                        logger.error("Broker connection timeout - broker did not become healthy within 60 seconds")
                        self._connection_manager.stop()
                        self._connection_manager = None
                        return orders_pb2.InitResponse(
                            success=False,
                            message="Failed to initialize strategy: Broker did not become healthy within timeout",
                        )
                else:
                    logger.error("Failed to establish initial broker connection")
                    self._connection_manager.stop()
                    self._connection_manager = None
                    return orders_pb2.InitResponse(
                        success=False,
                        message="Failed to initialize strategy: Could not establish broker connection",
                    )

            # Convert proto config to dict and get symbols
            config = dict(request.config) if request.config else {}
            symbols = list(request.symbols)

            # Initialize the strategy
            self.strategy._initialize(config, symbols, request.strategy_id)
            self._initialized = True

            # Return success response
            message = "Strategy initialized successfully"
            if broker_status not in ["connected", "not configured"]:
                message = f"Strategy initialized in observation mode (broker {broker_status})"

            response = orders_pb2.InitResponse(
                success=True,
                message=message,
            )

            # Add capability information
            response.capabilities["supports_options"] = "false"
            response.capabilities["supports_crypto"] = "false"
            response.capabilities["supports_fractional_shares"] = "true"
            response.capabilities["version"] = "1.0.0"
            response.capabilities["broker_status"] = broker_status
            response.capabilities["order_placement_enabled"] = str(self.strategy.is_broker_available).lower()

            return response

        except Exception as e:
            logger.error(f"Error initializing strategy: {e}", exc_info=True)
            return orders_pb2.InitResponse(
                success=False,
                message=f"Failed to initialize strategy: {str(e)}",
            )

    def Shutdown(self, request: orders_pb2.ShutdownRequest, context: grpc.ServicerContext) -> orders_pb2.ShutdownResponse:
        """Shutdown the strategy gracefully.

        Args:
            request: Shutdown request
            context: gRPC context

        Returns:
            ShutdownResponse indicating success or failure
        """
        try:
            logger.info(f"Shutting down strategy: {request.reason}")

            # Shutdown the strategy
            self.strategy._shutdown()

            # Signal the server to shutdown
            self._shutdown_event.set()

            return orders_pb2.ShutdownResponse(
                success=True,
                message="Strategy shutdown successfully",
            )

        except Exception as e:
            logger.error(f"Error shutting down strategy: {e}", exc_info=True)
            return orders_pb2.ShutdownResponse(
                success=False,
                message=f"Failed to shutdown strategy: {str(e)}",
            )

    def wait_for_shutdown(self) -> None:
        """Wait for the shutdown signal."""
        self._shutdown_event.wait()

    def _on_broker_connected(self, channel: grpc.Channel) -> None:
        """Handle broker connection established.

        Args:
            channel: The connected gRPC channel
        """
        with self._broker_stub_lock:
            broker_stub = TektiiBrokerStub(channel)  # type: ignore[no-untyped-call]
            self.strategy._set_broker_stub(broker_stub)
            logger.info("Broker connection established - order placement enabled")

    def _on_broker_disconnected(self) -> None:
        """Handle broker connection lost."""
        with self._broker_stub_lock:
            self.strategy._set_broker_stub(None)
            logger.warning("Broker connection lost - order placement disabled")

    def shutdown(self) -> None:
        """Shutdown the service and clean up resources."""
        if self._connection_manager:
            self._connection_manager.stop()


def serve(strategy_class: Type[TektiiStrategy], port: int = 50051, broker_address: Optional[str] = None) -> None:
    """Run the gRPC server for the strategy.

    This function starts a gRPC server that listens for events from the
    trading engine and routes them to the strategy.

    Args:
        strategy_class: The strategy class to instantiate
        port: The port to listen on (default: 50051)
        broker_address: Optional address of the broker service (e.g., "localhost:50052")
    """

    def signal_handler(sig: int, frame: Any) -> None:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create strategy instance
    strategy = strategy_class()

    # Create service with broker address
    service = TektiiStrategyService(strategy, broker_address)

    # Note: The connection to the broker will be established when Initialize is called,
    # ensuring proper startup sequencing

    # Create and start server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TektiiStrategyServicer_to_server(service, server)  # type: ignore[no-untyped-call]

    # Add health check service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("tektii.strategy", health_pb2.HealthCheckResponse.SERVING)

    # Start server
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    logger.info(f"Strategy server started on port {port}")
    if broker_address:
        logger.info(f"Broker address configured: {broker_address}")
        logger.info("Waiting for Initialize call to establish broker connection...")
    else:
        logger.warning("No broker address provided - strategy will run in standalone mode")

    # Wait for shutdown
    try:
        service.wait_for_shutdown()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")

    # Graceful shutdown
    server.stop(grace=5)
    logger.info("Server stopped")

    # Shutdown service (closes connection manager)
    service.shutdown()
    logger.info("Service shutdown complete")
