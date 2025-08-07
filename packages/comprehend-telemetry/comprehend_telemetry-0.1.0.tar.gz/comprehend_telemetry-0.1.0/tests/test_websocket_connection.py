"""Tests for WebSocketConnection class."""

import json
import threading
import time
from unittest.mock import Mock, MagicMock, patch, call
import pytest

from comprehend_telemetry.websocket_connection import WebSocketConnection
from comprehend_telemetry.wire_protocol import (
    InitMessage,
    NewObservedServiceMessage,
    NewObservedHttpRouteMessage,
    ObservationMessage,
    HttpServerObservation,
)


class TestWebSocketConnection:
    """Test cases for WebSocketConnection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.log_messages = []
        self.mock_logger = Mock(side_effect=lambda msg: self.log_messages.append(msg))
        self.mock_socket = Mock()
        self.mock_socket_class = Mock(return_value=self.mock_socket)

        # Mock threading to avoid actual threading in tests
        self.mock_thread = Mock()
        self.mock_thread_class = Mock(return_value=self.mock_thread)
        self.mock_timer = Mock()
        self.mock_timer_class = Mock(return_value=self.mock_timer)

    def test_connection_establishment(self):
        """Test WebSocket connection creation with correct URL."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Should create WebSocket with correct URL
            self.mock_socket_class.assert_called_once()
            call_args = self.mock_socket_class.call_args
            assert call_args[0][0] == 'wss://ingestion.comprehend.dev/test-org/observations'

            # Should set up event handlers
            call_kwargs = call_args[1]
            assert 'on_open' in call_kwargs
            assert 'on_message' in call_kwargs
            assert 'on_close' in call_kwargs
            assert 'on_error' in call_kwargs

            # Should start connection thread
            self.mock_thread_class.assert_called_once()
            thread_kwargs = self.mock_thread_class.call_args[1]
            assert thread_kwargs['daemon'] is True
            self.mock_thread.start.assert_called_once()

            connection.close()

    def test_connection_without_logger(self):
        """Test connection works without logger."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token')
            assert connection.logger is None
            connection.close()

    def test_on_open_sends_init_message(self):
        """Test that init message is sent on connection open."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Get the on_open handler and call it
            on_open = self.mock_socket_class.call_args[1]['on_open']
            on_open(self.mock_socket)

            # Should send init message
            self.mock_socket.send.assert_called_once()
            sent_data = self.mock_socket.send.call_args[0][0]
            sent_message = json.loads(sent_data)

            assert sent_message['event'] == 'init'
            assert sent_message['protocolVersion'] == 1
            assert sent_message['token'] == 'test-token'
            assert 'WebSocket connected. Sending init/auth message.' in self.log_messages

            connection.close()

    def test_authorization_acknowledgment(self):
        """Test handling of authorization acknowledgment."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Get the on_message handler
            on_message = self.mock_socket_class.call_args[1]['on_message']

            # Send authorization acknowledgment
            auth_ack = json.dumps({'type': 'ack-authorized'})
            on_message(self.mock_socket, auth_ack)

            assert connection.authorized is True
            assert 'Authorization acknowledged by server.' in self.log_messages

            connection.close()

    def test_message_queuing_and_replay(self):
        """Test message queuing before authorization and replay after."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Clear any init messages
            self.mock_socket.send.reset_mock()

            # Send messages before authorization
            service_message = NewObservedServiceMessage(
                event='new-entity',
                type='service',
                hash='test-hash-1',
                name='test-service'
            )

            observation_message = ObservationMessage(
                event='observations',
                seq=1,
                observations=[HttpServerObservation(
                    type='http-server',
                    subject='test-subject',
                    timestamp=1700000000000000000,  # nanoseconds
                    path='/test',
                    status=200,
                    duration=100000000  # nanoseconds
                )]
            )

            connection.send_message(service_message)
            connection.send_message(observation_message)

            # Should not send immediately (not authorized yet)
            self.mock_socket.send.assert_not_called()

            # Get the on_message handler and authorize
            on_message = self.mock_socket_class.call_args[1]['on_message']
            auth_ack = json.dumps({'type': 'ack-authorized'})
            on_message(self.mock_socket, auth_ack)

            # Should replay both messages
            assert self.mock_socket.send.call_count == 2

            connection.close()

    def test_send_messages_immediately_when_authorized(self):
        """Test messages are sent immediately when already authorized."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Authorize first
            on_message = self.mock_socket_class.call_args[1]['on_message']
            auth_ack = json.dumps({'type': 'ack-authorized'})
            on_message(self.mock_socket, auth_ack)

            # Clear previous calls
            self.mock_socket.send.reset_mock()

            # Send message
            service_message = NewObservedServiceMessage(
                event='new-entity',
                type='service',
                hash='test-hash',
                name='test-service'
            )

            connection.send_message(service_message)

            # Should send immediately
            self.mock_socket.send.assert_called_once()

            connection.close()

    def test_entity_acknowledgment_handling(self):
        """Test handling of entity acknowledgments."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Authorize and send messages
            on_message = self.mock_socket_class.call_args[1]['on_message']
            auth_ack = json.dumps({'type': 'ack-authorized'})
            on_message(self.mock_socket, auth_ack)

            service_message = NewObservedServiceMessage(
                event='new-entity',
                type='service',
                hash='service-hash',
                name='test-service'
            )

            route_message = NewObservedHttpRouteMessage(
                event='new-entity',
                type='http-route',
                hash='route-hash',
                parent='service-hash',
                method='GET',
                route='/test'
            )

            connection.send_message(service_message)
            connection.send_message(route_message)

            # Acknowledge service message
            ack_observed = json.dumps({'type': 'ack-observed', 'hash': 'service-hash'})
            on_message(self.mock_socket, ack_observed)

            # Should remove from unacknowledged
            assert 'service-hash' not in connection.unacknowledged_observed
            assert 'route-hash' in connection.unacknowledged_observed

            connection.close()

    def test_observation_acknowledgment_handling(self):
        """Test handling of observation acknowledgments."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Authorize and send messages
            on_message = self.mock_socket_class.call_args[1]['on_message']
            auth_ack = json.dumps({'type': 'ack-authorized'})
            on_message(self.mock_socket, auth_ack)

            obs1 = ObservationMessage(event='observations', seq=1, observations=[])
            obs2 = ObservationMessage(event='observations', seq=2, observations=[])

            connection.send_message(obs1)
            connection.send_message(obs2)

            # Acknowledge first observation
            ack_obs = json.dumps({'type': 'ack-observations', 'seq': 1})
            on_message(self.mock_socket, ack_obs)

            # Should remove seq 1 but keep seq 2
            assert 1 not in connection.unacknowledged_observations
            assert 2 in connection.unacknowledged_observations

            connection.close()

    def test_reconnection_on_close(self):
        """Test automatic reconnection on close."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Timer', self.mock_timer_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Get the on_close handler and call it
            on_close = self.mock_socket_class.call_args[1]['on_close']
            on_close(self.mock_socket, 1000, 'Normal closure')

            # Should log disconnection
            assert 'WebSocket disconnected. Code: 1000, Reason: Normal closure' in self.log_messages

            # Should schedule reconnection timer
            self.mock_timer_class.assert_called_once()
            timer_args = self.mock_timer_class.call_args
            assert timer_args[0][0] == 1.0  # delay
            self.mock_timer.start.assert_called_once()

            # Should reset authorization
            assert connection.authorized is False

            connection.close()

    def test_authorization_reset_on_close(self):
        """Test authorization state is reset on close."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Timer', self.mock_timer_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Authorize first
            on_message = self.mock_socket_class.call_args[1]['on_message']
            auth_ack = json.dumps({'type': 'ack-authorized'})
            on_message(self.mock_socket, auth_ack)
            assert connection.authorized is True

            # Close connection
            on_close = self.mock_socket_class.call_args[1]['on_close']
            on_close(self.mock_socket, 1000, 'test')

            # Should reset authorization
            assert connection.authorized is False

            connection.close()

    def test_no_reconnect_when_explicitly_closed(self):
        """Test no reconnection when explicitly closed."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Timer', self.mock_timer_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Explicitly close
            connection.close()

            # Get the on_close handler and call it (simulating WebSocket close)
            on_close = self.mock_socket_class.call_args[1]['on_close']
            on_close(self.mock_socket, 1000, 'Explicit close')

            # Should not schedule reconnection
            self.mock_timer_class.assert_not_called()

    def test_websocket_error_logging(self):
        """Test WebSocket error logging."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Get the on_error handler and call it
            on_error = self.mock_socket_class.call_args[1]['on_error']
            test_error = Exception('Connection failed')
            on_error(self.mock_socket, test_error)

            assert 'WebSocket encountered an error: Connection failed' in self.log_messages

            connection.close()

    def test_malformed_message_handling(self):
        """Test handling of malformed server messages."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Get the on_message handler
            on_message = self.mock_socket_class.call_args[1]['on_message']

            # Send malformed JSON
            on_message(self.mock_socket, '{invalid json}')

            # Should log error (message content varies by Python version)
            error_logged = any('Error parsing message from server:' in msg
                             for msg in self.log_messages)
            assert error_logged

            connection.close()

    def test_connection_close_and_cleanup(self):
        """Test proper connection close and cleanup."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            connection.close()

            # Should close socket
            self.mock_socket.close.assert_called_once()
            # Should disable reconnection
            assert connection.should_reconnect is False

    def test_send_when_socket_unavailable(self):
        """Test sending messages when socket is unavailable."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)
            connection.authorized = True

            # Make socket.send raise exception
            self.mock_socket.send.side_effect = Exception('Connection closed')

            service_message = NewObservedServiceMessage(
                event='new-entity',
                type='service',
                hash='test-hash',
                name='test-service'
            )

            # Should not raise exception
            connection.send_message(service_message)

            connection.close()

    def test_message_types_queuing(self):
        """Test different message types are queued correctly."""
        with patch('comprehend_telemetry.websocket_connection.websocket.WebSocketApp', self.mock_socket_class), \
             patch('comprehend_telemetry.websocket_connection.threading.Thread', self.mock_thread_class):

            connection = WebSocketConnection('test-org', 'test-token', self.mock_logger)

            # Test entity message queuing
            service_msg = NewObservedServiceMessage(
                event='new-entity',
                type='service',
                hash='service-hash',
                name='test-service'
            )
            connection.send_message(service_msg)
            assert 'service-hash' in connection.unacknowledged_observed

            # Test interaction message queuing
            route_msg = NewObservedHttpRouteMessage(
                event='new-entity',
                type='http-route',
                hash='route-hash',
                parent='service-hash',
                method='GET',
                route='/test'
            )
            connection.send_message(route_msg)
            assert 'route-hash' in connection.unacknowledged_observed

            # Test observation message queuing
            obs_msg = ObservationMessage(event='observations', seq=1, observations=[])
            connection.send_message(obs_msg)
            assert 1 in connection.unacknowledged_observations

            connection.close()