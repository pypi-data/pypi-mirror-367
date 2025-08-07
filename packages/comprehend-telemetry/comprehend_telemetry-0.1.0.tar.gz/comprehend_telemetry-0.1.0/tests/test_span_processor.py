"""Tests for ComprehendDevSpanProcessor."""

from unittest.mock import Mock, patch, MagicMock
import pytest
from typing import Dict, Any, Optional

from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.resources import Resource

from comprehend_telemetry.span_processor import ComprehendDevSpanProcessor
from comprehend_telemetry.sql_analyzer import SQLAnalysisResult
from comprehend_telemetry.wire_protocol import (
    NewObservedServiceMessage,
    NewObservedHttpRouteMessage,
    ObservationMessage,
    HttpServerObservation
)


class TestComprehendDevSpanProcessor:
    """Test cases for ComprehendDevSpanProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sent_messages = []
        self.mock_connection = Mock()
        self.mock_connection.send_message = Mock(side_effect=lambda msg: self.sent_messages.append(msg))
        self.mock_connection.close = Mock()

    def create_mock_span(
        self,
        name: str = "test-span",
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
        resource_attributes: Optional[Dict[str, Any]] = None,
        status_code: StatusCode = StatusCode.OK,
        status_description: str = "",
        events: Optional[list] = None,
        start_time: int = 1700000000000000000,  # nanoseconds
        end_time: Optional[int] = None,
    ) -> ReadableSpan:
        """Create a mock ReadableSpan for testing."""
        if attributes is None:
            attributes = {}
        if resource_attributes is None:
            resource_attributes = {'service.name': 'test-service'}
        if events is None:
            events = []
        if end_time is None:
            end_time = start_time + 100000000  # 100ms later

        mock_span = Mock(spec=ReadableSpan)
        mock_span.name = name
        mock_span.kind = kind
        mock_span.attributes = attributes
        mock_span.resource = Mock()
        mock_span.resource.attributes = resource_attributes
        mock_span.status = Mock()
        mock_span.status.status_code = status_code
        mock_span.status.description = status_description
        mock_span.events = events
        mock_span.start_time = start_time
        mock_span.end_time = end_time

        return mock_span

    def test_service_discovery(self):
        """Test service discovery and registration."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                resource_attributes={
                    'service.name': 'my-api',
                    'service.namespace': 'production',
                    'deployment.environment': 'prod'
                }
            )

            processor.on_end(span)

            assert len(self.sent_messages) == 1
            service_msg = self.sent_messages[0]
            assert isinstance(service_msg, NewObservedServiceMessage)
            assert service_msg.event == 'new-entity'
            assert service_msg.type == 'service'
            assert service_msg.name == 'my-api'
            assert service_msg.namespace == 'production'
            assert service_msg.environment == 'prod'
            assert service_msg.hash is not None

            processor.shutdown()

    def test_service_discovery_no_duplicates(self):
        """Test that services are not duplicated."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span1 = self.create_mock_span(
                resource_attributes={'service.name': 'my-api'}
            )
            span2 = self.create_mock_span(
                resource_attributes={'service.name': 'my-api'}
            )

            processor.on_end(span1)
            processor.on_end(span2)

            # Should only send one service registration
            service_messages = [msg for msg in self.sent_messages
                              if hasattr(msg, 'event') and msg.event == 'new-entity' and msg.type == 'service']
            assert len(service_messages) == 1

            processor.shutdown()

    def test_service_without_namespace_environment(self):
        """Test service discovery without namespace and environment."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                resource_attributes={'service.name': 'simple-service'}
            )

            processor.on_end(span)

            service_msg = self.sent_messages[0]
            assert service_msg.name == 'simple-service'
            assert service_msg.namespace is None
            assert service_msg.environment is None

            processor.shutdown()

    def test_ignore_spans_without_service_name(self):
        """Test ignoring spans without service.name."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(resource_attributes={})

            processor.on_end(span)

            assert len(self.sent_messages) == 0

            processor.shutdown()

    def test_http_server_span_processing(self):
        """Test processing HTTP server spans."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/users/{id}',
                    'http.method': 'GET',
                    'http.target': '/api/users/123',
                    'http.status_code': 200
                }
            )

            processor.on_end(span)

            # Should have service + route + observation messages
            assert len(self.sent_messages) == 3

            # Check service message
            service_msg = self.sent_messages[0]
            assert service_msg.type == 'service'

            # Check route message
            route_msg = self.sent_messages[1]
            assert isinstance(route_msg, NewObservedHttpRouteMessage)
            assert route_msg.event == 'new-entity'
            assert route_msg.type == 'http-route'
            assert route_msg.method == 'GET'
            assert route_msg.route == '/api/users/{id}'

            # Check observation message
            obs_msg = self.sent_messages[2]
            assert isinstance(obs_msg, ObservationMessage)
            assert obs_msg.event == 'observations'
            assert len(obs_msg.observations) == 1

            observation = obs_msg.observations[0]
            assert isinstance(observation, HttpServerObservation)
            assert observation.type == 'http-server'
            assert observation.path == '/api/users/123'
            assert observation.status == 200

            processor.shutdown()

    def test_http_url_path_extraction(self):
        """Test extracting path from http.url when http.target is not available."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/test',
                    'http.method': 'POST',
                    'http.url': 'https://example.com/api/test?param=value',
                    'http.status_code': 201
                }
            )

            processor.on_end(span)

            obs_msg = [msg for msg in self.sent_messages if hasattr(msg, 'observations')][0]
            observation = obs_msg.observations[0]
            assert observation.path == '/api/test'

            processor.shutdown()

    def test_relative_url_handling(self):
        """Test handling of relative URLs in http.target."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/test',
                    'http.method': 'GET',
                    'http.target': 'invalid-url',
                    'http.status_code': 400
                }
            )

            processor.on_end(span)

            obs_msg = [msg for msg in self.sent_messages if hasattr(msg, 'observations')][0]
            observation = obs_msg.observations[0]
            # When used with placeholder base, 'invalid-url' becomes '/invalid-url'
            assert observation.path == '/invalid-url'

            processor.shutdown()

    def test_http_optional_attributes(self):
        """Test including optional HTTP attributes when present."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/upload',
                    'http.method': 'POST',
                    'http.target': '/api/upload',
                    'http.status_code': 200,
                    'http.flavor': '1.1',
                    'http.user_agent': 'Mozilla/5.0',
                    'http.request_content_length': 1024,
                    'http.response_content_length': 256
                }
            )

            processor.on_end(span)

            obs_msg = [msg for msg in self.sent_messages if hasattr(msg, 'observations')][0]
            observation = obs_msg.observations[0]
            assert observation.httpVersion == '1.1'
            assert observation.userAgent == 'Mozilla/5.0'
            assert observation.requestBytes == 1024
            assert observation.responseBytes == 256

            processor.shutdown()

    def test_no_duplicate_routes(self):
        """Test that routes are not duplicated."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span1 = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/users',
                    'http.method': 'GET',
                    'http.status_code': 200
                }
            )
            span2 = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/users',
                    'http.method': 'GET',
                    'http.status_code': 200
                }
            )

            processor.on_end(span1)
            processor.on_end(span2)

            route_messages = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'http-route']
            assert len(route_messages) == 1

            processor.shutdown()

    def test_http_client_processing(self):
        """Test processing HTTP client spans."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.CLIENT,
                attributes={
                    'http.url': 'https://api.external.com/v1/data',
                    'http.method': 'GET',
                    'http.status_code': 200
                }
            )

            processor.on_end(span)

            # Should have service + http-service + http-request + observation
            assert len(self.sent_messages) == 4

            http_service_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'http-service'][0]
            assert http_service_msg.event == 'new-entity'
            assert http_service_msg.type == 'http-service'
            assert http_service_msg.protocol == 'https'
            assert http_service_msg.host == 'api.external.com'
            assert http_service_msg.port == 443

            http_request_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'http-request'][0]
            assert http_request_msg.event == 'new-interaction'
            assert http_request_msg.type == 'http-request'

            obs_msg = [msg for msg in self.sent_messages if hasattr(msg, 'observations')][0]
            observation = obs_msg.observations[0]
            assert observation.type == 'http-client'
            assert observation.path == '/v1/data'
            assert observation.method == 'GET'
            assert observation.status == 200

            processor.shutdown()

    def test_http_port_handling(self):
        """Test HTTP and HTTPS port handling."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            http_span = self.create_mock_span(
                kind=SpanKind.CLIENT,
                attributes={
                    'http.url': 'http://api.example.com/test',
                    'http.method': 'GET'
                }
            )

            processor.on_end(http_span)

            http_service_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'http-service'][0]
            assert http_service_msg.protocol == 'http'
            assert http_service_msg.host == 'api.example.com'
            assert http_service_msg.port == 80

            processor.shutdown()

    def test_custom_ports(self):
        """Test handling of custom ports."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.CLIENT,
                attributes={
                    'http.url': 'https://api.example.com:8443/test',
                    'http.method': 'POST'
                }
            )

            processor.on_end(span)

            http_service_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'http-service'][0]
            assert http_service_msg.protocol == 'https'
            assert http_service_msg.host == 'api.example.com'
            assert http_service_msg.port == 8443

            processor.shutdown()

    def test_client_spans_without_method(self):
        """Test client spans without http.method are not processed for observations."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                kind=SpanKind.CLIENT,
                attributes={
                    'http.url': 'https://api.example.com/test'
                    # Missing http.method
                }
            )

            processor.on_end(span)

            # Should still create service and interaction, but no observation
            observation_messages = [msg for msg in self.sent_messages if hasattr(msg, 'observations')]
            assert len(observation_messages) == 0

            processor.shutdown()

    @patch('comprehend_telemetry.span_processor.analyze_sql')
    def test_database_processing(self, mock_analyze_sql):
        """Test processing database spans."""
        mock_analyze_sql.return_value = SQLAnalysisResult(
            table_operations={'users': ['SELECT']},
            normalized_query='SELECT * FROM users',
            presentable_query='SELECT * FROM users'
        )

        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                attributes={
                    'db.system': 'postgresql',
                    'db.name': 'myapp',
                    'net.peer.name': 'db.example.com',
                    'net.peer.port': 5432
                }
            )

            processor.on_end(span)

            database_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'database'][0]
            assert database_msg.event == 'new-entity'
            assert database_msg.type == 'database'
            assert database_msg.system == 'postgresql'
            assert database_msg.name == 'myapp'
            assert database_msg.host == 'db.example.com'
            assert database_msg.port == 5432

            processor.shutdown()

    @patch('comprehend_telemetry.span_processor.analyze_sql')
    def test_database_connection_strings(self, mock_analyze_sql):
        """Test processing database connection strings."""
        mock_analyze_sql.return_value = SQLAnalysisResult(
            table_operations={},
            normalized_query='',
            presentable_query=''
        )

        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                attributes={
                    'db.system': 'postgresql',
                    'db.connection_string': 'postgresql://user:password@localhost:5432/testdb'
                }
            )

            processor.on_end(span)

            database_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'database'][0]
            assert database_msg.system == 'postgresql'
            assert database_msg.host == 'localhost'
            assert database_msg.port == 5432
            assert database_msg.name == 'testdb'

            connection_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'db-connection'][0]
            assert connection_msg.event == 'new-interaction'
            assert connection_msg.type == 'db-connection'
            assert connection_msg.user == 'user'

            processor.shutdown()

    @patch('comprehend_telemetry.span_processor.analyze_sql')
    def test_sql_query_processing(self, mock_analyze_sql):
        """Test processing SQL queries."""
        mock_analyze_sql.return_value = SQLAnalysisResult(
            table_operations={'users': ['SELECT']},
            normalized_query='SELECT * FROM users',
            presentable_query='SELECT * FROM users'
        )

        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                attributes={
                    'db.system': 'postgresql',
                    'db.statement': 'SELECT * FROM users WHERE id = $1',
                    'db.name': 'myapp',
                    'net.peer.name': 'localhost',
                    'db.response.returned_rows': 1
                }
            )

            processor.on_end(span)

            mock_analyze_sql.assert_called_once_with('SELECT * FROM users WHERE id = $1')

            query_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'db-query'][0]
            assert query_msg.event == 'new-interaction'
            assert query_msg.type == 'db-query'
            assert query_msg.query == 'SELECT * FROM users'
            assert query_msg.selects == ['users']

            obs_msg = [msg for msg in self.sent_messages if hasattr(msg, 'observations')][0]
            observation = obs_msg.observations[0]
            assert observation.type == 'db-query'
            assert observation.returnedRows == 1

            processor.shutdown()

    @patch('comprehend_telemetry.span_processor.analyze_sql')
    def test_multiple_table_operations(self, mock_analyze_sql):
        """Test handling multiple table operations in SQL."""
        mock_analyze_sql.return_value = SQLAnalysisResult(
            table_operations={
                'users': ['SELECT'],
                'orders': ['INSERT'],
                'products': ['UPDATE']
            },
            normalized_query='INSERT INTO orders SELECT * FROM users UPDATE products',
            presentable_query='INSERT INTO orders SELECT * FROM users UPDATE products'
        )

        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                attributes={
                    'db.system': 'mysql',
                    'db.statement': 'INSERT INTO orders SELECT * FROM users; UPDATE products SET stock = 0',
                    'db.name': 'ecommerce'
                }
            )

            processor.on_end(span)

            query_msg = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'db-query'][0]
            assert query_msg.selects == ['users']
            assert query_msg.inserts == ['orders']
            assert query_msg.updates == ['products']

            processor.shutdown()

    def test_non_sql_database_systems(self):
        """Test not processing SQL for non-SQL database systems."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection), \
             patch('comprehend_telemetry.span_processor.analyze_sql') as mock_analyze_sql:

            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            span = self.create_mock_span(
                attributes={
                    'db.system': 'mongodb',
                    'db.statement': 'db.users.find({_id: ObjectId("...")})',
                    'db.name': 'myapp'
                }
            )

            processor.on_end(span)

            mock_analyze_sql.assert_not_called()

            # Should still create database and connection, but no query interaction
            query_messages = [msg for msg in self.sent_messages if hasattr(msg, 'type') and msg.type == 'db-query']
            assert len(query_messages) == 0

            processor.shutdown()

    def test_error_handling_from_exception_events(self):
        """Test extracting error information from exception events."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')

            exception_event = Mock()
            exception_event.name = 'exception'
            exception_event.attributes = {
                'exception.message': 'Database connection failed',
                'exception.type': 'ConnectionError',
                'exception.stacktrace': 'Error at line 42\n  at method()'
            }

            span = self.create_mock_span(
                kind=SpanKind.SERVER,
                attributes={
                    'http.route': '/api/error',
                    'http.method': 'GET',
                    'http.status_code': 500
                },
                status_code=StatusCode.ERROR,
                status_description='Internal server error',
                events=[exception_event]
            )

            processor.on_end(span)

            obs_msg = [msg for msg in self.sent_messages if hasattr(msg, 'observations')][0]
            observation = obs_msg.observations[0]
            assert observation.errorMessage == 'Database connection failed'
            assert observation.errorType == 'ConnectionError'
            assert observation.stack == 'Error at line 42\n  at method()'

            processor.shutdown()

    def test_debug_logging(self):
        """Test debug logging functionality."""
        mock_logger = Mock()

        with patch('comprehend_telemetry.span_processor.WebSocketConnection') as mock_ws_class:
            processor = ComprehendDevSpanProcessor('test-org', 'test-token', debug=mock_logger)
            mock_ws_class.assert_called_once_with('test-org', 'test-token', mock_logger)
            processor.shutdown()

    def test_debug_logging_boolean(self):
        """Test debug logging with boolean value."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection') as mock_ws_class, \
             patch('builtins.print') as mock_print:
            processor = ComprehendDevSpanProcessor('test-org', 'test-token', debug=True)
            mock_ws_class.assert_called_once_with('test-org', 'test-token', mock_print)
            processor.shutdown()

    def test_debug_logging_disabled(self):
        """Test debug logging disabled."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection') as mock_ws_class:
            processor = ComprehendDevSpanProcessor('test-org', 'test-token', debug=False)
            mock_ws_class.assert_called_once_with('test-org', 'test-token', None)
            processor.shutdown()

    def test_shutdown_closes_connection(self):
        """Test that shutdown closes the connection."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')
            result = processor.shutdown()
            assert result is True
            self.mock_connection.close.assert_called_once()

    def test_force_flush(self):
        """Test force flush returns True."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')
            result = processor.force_flush()
            assert result is True
            processor.shutdown()

    def test_on_start_is_noop(self):
        """Test that on_start is a no-op."""
        with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=self.mock_connection):
            processor = ComprehendDevSpanProcessor('test-org', 'test-token')
            # Should not raise any exception
            processor.on_start(Mock(), Mock())
            processor.shutdown()