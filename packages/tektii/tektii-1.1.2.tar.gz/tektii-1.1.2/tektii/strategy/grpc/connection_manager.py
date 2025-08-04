"""Connection manager for maintaining gRPC broker connections.

This module provides robust connection management with health monitoring,
automatic reconnection, and connection state tracking.
"""

import logging
import threading
import time
from enum import Enum
from typing import Any, Callable, Optional

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection state enumeration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"


class BrokerConnectionManager:
    """Manages the gRPC connection to the broker with health monitoring and reconnection."""

    def __init__(
        self,
        broker_address: str,
        on_connected: Optional[Callable[[grpc.Channel], None]] = None,
        on_disconnected: Optional[Callable[[], None]] = None,
        health_check_interval: float = 5.0,
        reconnect_interval: float = 2.0,
        max_reconnect_attempts: int = -1,  # -1 for infinite
    ):
        """Initialize the connection manager.

        Args:
            broker_address: The broker service address (e.g., "localhost:50052")
            on_connected: Callback when connection is established
            on_disconnected: Callback when connection is lost
            health_check_interval: Seconds between health checks
            reconnect_interval: Base seconds between reconnection attempts
            max_reconnect_attempts: Maximum reconnection attempts (-1 for infinite)
        """
        self.broker_address = broker_address
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.health_check_interval = health_check_interval
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts

        self._channel: Optional[grpc.Channel] = None
        self._state = ConnectionState.DISCONNECTED
        self._state_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._health_thread: Optional[threading.Thread] = None
        self._reconnect_attempts = 0

    @property
    def state(self) -> ConnectionState:
        """Get the current connection state."""
        with self._state_lock:
            return self._state

    @property
    def channel(self) -> Optional[grpc.Channel]:
        """Get the current channel if connected."""
        with self._state_lock:
            if self._state == ConnectionState.CONNECTED:
                return self._channel
            return None

    def _set_state(self, new_state: ConnectionState) -> None:
        """Set the connection state with proper locking."""
        with self._state_lock:
            if self._state != new_state:
                logger.info(f"Connection state changed: {self._state.value} -> {new_state.value}")
                self._state = new_state

    def _create_channel(self) -> grpc.Channel:
        """Create a new gRPC channel with appropriate options."""
        options: list[tuple[str, Any]] = [
            ("grpc.keepalive_time_ms", 10000),  # Send keepalive every 10 seconds
            ("grpc.keepalive_timeout_ms", 5000),  # Timeout after 5 seconds
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.enable_retries", 1),
            ("grpc.max_connection_idle_ms", 300000),  # 5 minutes
        ]
        return grpc.insecure_channel(self.broker_address, options=options)

    def _check_health(self, service_name: str = "") -> bool:
        """Check if the broker connection is healthy.

        Args:
            service_name: Optional service name to check. Empty string checks overall server health.
        """
        if not self._channel:
            return False

        try:
            # Use gRPC health check protocol
            health_stub = health_pb2_grpc.HealthStub(self._channel)
            request = health_pb2.HealthCheckRequest(service=service_name)
            logger.debug(f"Sending health check request for service: '{service_name or 'overall'}'")
            response = health_stub.Check(request, timeout=3.0)
            is_serving = response.status == health_pb2.HealthCheckResponse.SERVING
            if is_serving:
                logger.info(f"Health check succeeded for service '{service_name or 'overall'}' - status: SERVING")
            else:
                logger.warning(f"Health check returned non-serving status for '{service_name or 'overall'}': {response.status}")
            return bool(is_serving)
        except Exception as e:
            logger.debug(f"Health check failed for service '{service_name}': {type(e).__name__}: {e}")
            return False

    def _connect(self) -> bool:
        """Attempt to establish connection to the broker."""
        try:
            self._set_state(ConnectionState.CONNECTING)

            # Close existing channel if any
            if self._channel:
                self._channel.close()

            # Create new channel
            self._channel = self._create_channel()

            # Wait for channel to be ready
            logger.info(f"Waiting for gRPC channel to be ready at {self.broker_address}...")
            future = grpc.channel_ready_future(self._channel)
            future.result(timeout=10.0)  # Increased timeout
            logger.info("gRPC channel is ready, checking health service...")

            # Verify with health check - retry a few times as health service might not be immediately ready
            health_check_retries = 10  # More retries
            health_check_delay = 2.0  # Longer delay between retries

            logger.info("Starting health check verification...")
            for attempt in range(health_check_retries):
                logger.info(f"Health check attempt {attempt + 1}/{health_check_retries}")
                # Use standard gRPC health check (empty service name checks overall server health)
                if self._check_health(""):
                    self._set_state(ConnectionState.CONNECTED)
                    self._reconnect_attempts = 0
                    logger.info(f"Successfully connected to broker at {self.broker_address}")

                    # Notify callback
                    if self.on_connected:
                        self.on_connected(self._channel)

                    return True

                if attempt < health_check_retries - 1:
                    logger.info(f"Health check attempt {attempt + 1}/{health_check_retries} failed, retrying in {health_check_delay}s...")
                    time.sleep(health_check_delay)

            raise Exception(f"Health check failed after {health_check_retries} attempts")

        except Exception as e:
            logger.error(f"Failed to connect to broker at {self.broker_address}: {type(e).__name__}: {e}")
            self._set_state(ConnectionState.FAILED)
            if self._channel:
                self._channel.close()
                self._channel = None
            return False

    def _reconnect_loop(self) -> None:
        """Continuously attempt to reconnect when disconnected."""
        while not self._stop_event.is_set():
            if self._state in [ConnectionState.FAILED, ConnectionState.DISCONNECTED]:
                self._reconnect_attempts += 1

                if self.max_reconnect_attempts > 0 and self._reconnect_attempts > self.max_reconnect_attempts:
                    logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
                    break

                logger.info(f"Attempting to reconnect (attempt {self._reconnect_attempts})...")
                if self._connect():
                    # Connection successful, health monitoring will take over
                    break
                else:
                    # Exponential backoff with max of 60 seconds
                    wait_time = min(self.reconnect_interval * (2 ** (self._reconnect_attempts - 1)), 60)
                    logger.info(f"Waiting {wait_time:.1f}s before next reconnection attempt...")
                    self._stop_event.wait(wait_time)
            else:
                # Not in a failed state, exit reconnection loop
                break

    def _health_monitor_loop(self) -> None:
        """Monitor connection health and trigger reconnection if needed."""
        consecutive_failures = 0
        max_consecutive_failures = 5  # Increased from 3 to be more tolerant

        logger.info(f"Health monitor started - checking every {self.health_check_interval} seconds")

        while not self._stop_event.is_set():
            self._stop_event.wait(self.health_check_interval)

            if self._state == ConnectionState.CONNECTED:
                logger.debug("Performing periodic health check...")
                if self._check_health():
                    if consecutive_failures > 0:
                        logger.info(f"Health check recovered after {consecutive_failures} failures")
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    logger.warning(f"Health check failed ({consecutive_failures}/{max_consecutive_failures})")

                    if consecutive_failures >= max_consecutive_failures:
                        logger.error("Connection lost - triggering reconnection")
                        self._set_state(ConnectionState.DISCONNECTED)

                        # Notify callback
                        if self.on_disconnected:
                            self.on_disconnected()

                        # Start reconnection in a separate thread
                        reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True, name="BrokerReconnect")
                        reconnect_thread.start()

    def start(self) -> bool:
        """Start the connection manager and establish initial connection.

        Returns:
            True if initial connection successful, False otherwise
        """
        # Initial connection attempt
        if not self._connect():
            return False

        # Start health monitoring thread
        self._health_thread = threading.Thread(target=self._health_monitor_loop, daemon=True, name="BrokerHealthMonitor")
        self._health_thread.start()

        return True

    def stop(self) -> None:
        """Stop the connection manager and close connections."""
        logger.info("Stopping connection manager...")
        self._stop_event.set()

        # Wait for health thread to stop
        if self._health_thread and self._health_thread.is_alive():
            self._health_thread.join(timeout=5.0)

        # Close channel
        if self._channel:
            self._channel.close()
            self._channel = None

        self._set_state(ConnectionState.DISCONNECTED)
        logger.info("Connection manager stopped")

    def wait_for_connection(self, timeout: float = 30.0) -> bool:
        """Wait for the connection to be established.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if connected within timeout, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._state == ConnectionState.CONNECTED:
                return True
            time.sleep(0.1)
        return False
