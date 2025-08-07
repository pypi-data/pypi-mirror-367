"""WebSocket connection for comprehend.dev telemetry ingestion."""

import json
import threading
import time
from typing import Dict, Optional, Callable, Union
import websocket

from .wire_protocol import (
    InitMessage,
    NewObservedEntityMessage,
    NewObservedInteractionMessage,
    ObservationInputMessage,
    ObservationMessage,
    ObservationOutputMessage,
    serialize_message
)

INGESTION_ENDPOINT = "wss://ingestion.comprehend.dev"


class WebSocketConnection:
    """WebSocket connection with automatic reconnection and message acknowledgment."""

    def __init__(
        self,
        organization: str,
        token: str,
        logger: Optional[Callable[[str], None]] = None
    ):
        self.organization = organization
        self.token = token
        self.logger = logger
        self.unacknowledged_observed: Dict[str, Union[NewObservedEntityMessage, NewObservedInteractionMessage]] = {}
        self.unacknowledged_observations: Dict[int, ObservationMessage] = {}
        self.socket: Optional[websocket.WebSocketApp] = None
        self.reconnect_delay = 1.0
        self.should_reconnect = True
        self.authorized = False
        self._connection_thread: Optional[threading.Thread] = None
        self._reconnect_timer: Optional[threading.Timer] = None

        # Start connection
        self._connect()

    def _log(self, message: str) -> None:
        """Log a message if logger is provided."""
        if self.logger:
            self.logger(message)

    def _connect(self) -> None:
        """Establish WebSocket connection."""
        websocket_url = f"{INGESTION_ENDPOINT}/{self.organization}/observations"
        self._log(f"Attempting to connect to {websocket_url}...")

        self.socket = websocket.WebSocketApp(
            websocket_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error
        )

        # Start connection in background thread
        self._connection_thread = threading.Thread(
            target=self._run_connection,
            daemon=True
        )
        self._connection_thread.start()

    def _run_connection(self) -> None:
        """Run the WebSocket connection (blocking call in background thread)."""
        try:
            # run_forever is a blocking call that handles the WebSocket event loop
            self.socket.run_forever()
        except Exception as e:
            self._log(f"WebSocket connection error: {e}")

    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        """Handle WebSocket connection open."""
        self._log("WebSocket connected. Sending init/auth message.")
        init_message = InitMessage(
            event="init",
            protocolVersion=1,
            token=self.token
        )
        self._send_raw(init_message)

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            msg_data = json.loads(message)

            if msg_data.get("type") == "ack-authorized":
                self.authorized = True
                self._log("Authorization acknowledged by server.")

                # Replay queued messages
                for message_obj in self.unacknowledged_observed.values():
                    self._send_raw(message_obj)
                for message_obj in self.unacknowledged_observations.values():
                    self._send_raw(message_obj)

            elif msg_data.get("type") == "ack-observed":
                hash_val = msg_data.get("hash")
                if hash_val and hash_val in self.unacknowledged_observed:
                    del self.unacknowledged_observed[hash_val]

            elif msg_data.get("type") == "ack-observations":
                seq = msg_data.get("seq")
                if seq is not None and seq in self.unacknowledged_observations:
                    del self.unacknowledged_observations[seq]

        except Exception as e:
            error_msg = str(e) if isinstance(e, Exception) else str(e)
            self._log(f"Error parsing message from server: {error_msg}")

    def _on_close(self, ws: websocket.WebSocketApp, close_status_code: Optional[int], close_msg: Optional[str]) -> None:
        """Handle WebSocket connection close."""
        code = close_status_code or 0
        reason = close_msg or ""
        self._log(f"WebSocket disconnected. Code: {code}, Reason: {reason}")
        self.authorized = False

        if self.should_reconnect:
            # Schedule reconnection
            self._reconnect_timer = threading.Timer(self.reconnect_delay, self._connect)
            self._reconnect_timer.start()

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        """Handle WebSocket error."""
        self._log(f"WebSocket encountered an error: {error}")

    def _send_raw(self, message: ObservationInputMessage) -> None:
        """Send message directly through WebSocket if connected."""
        if self.socket:
            try:
                serialized = serialize_message(message)
                self.socket.send(serialized)
            except Exception:
                # Connection might be closed, ignore send errors
                pass

    def send_message(self, message: ObservationInputMessage) -> None:
        """Send message, queueing if not yet authorized."""
        # Queue message for acknowledgment tracking
        if hasattr(message, 'event'):
            if message.event == "new-entity" or message.event == "new-interaction":
                if hasattr(message, 'hash'):
                    self.unacknowledged_observed[message.hash] = message
            elif message.event == "observations":
                if hasattr(message, 'seq'):
                    self.unacknowledged_observations[message.seq] = message

        # Send immediately if authorized, otherwise it will be sent after authorization
        if self.authorized:
            self._send_raw(message)

    def close(self) -> None:
        """Close WebSocket connection and stop reconnection."""
        self.should_reconnect = False

        # Cancel any pending reconnection
        if self._reconnect_timer:
            self._reconnect_timer.cancel()
            self._reconnect_timer = None

        # Close socket
        if self.socket:
            self.socket.close()