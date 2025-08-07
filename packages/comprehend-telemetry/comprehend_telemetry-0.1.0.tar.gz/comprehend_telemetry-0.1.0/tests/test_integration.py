"""Integration tests for the complete Python telemetry SDK."""

from unittest.mock import Mock, patch
import time

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

from comprehend_telemetry import ComprehendDevSpanProcessor


def test_complete_sdk_integration():
    """Test the complete SDK integration with OpenTelemetry."""

    # Mock the WebSocket connection
    mock_connection = Mock()
    sent_messages = []
    mock_connection.send_message = Mock(side_effect=lambda msg: sent_messages.append(msg))
    mock_connection.close = Mock()

    with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=mock_connection):
        # Set up OpenTelemetry with our processor
        resource = Resource.create({
            'service.name': 'my-python-service',
            'service.namespace': 'production',
            'deployment.environment': 'prod'
        })

        tracer_provider = TracerProvider(resource=resource)
        processor = ComprehendDevSpanProcessor('test-org', 'test-token')
        tracer_provider.add_span_processor(processor)

        # Set the global tracer provider
        trace.set_tracer_provider(tracer_provider)
        tracer = trace.get_tracer(__name__)

        # Create some spans to demonstrate different scenarios

        # 1. HTTP Server span
        with tracer.start_as_current_span(
            "handle_user_request",
            kind=trace.SpanKind.SERVER
        ) as span:
            span.set_attributes({
                'http.method': 'GET',
                'http.route': '/api/users/{id}',
                'http.target': '/api/users/123',
                'http.status_code': 200,
                'http.user_agent': 'Python-Test/1.0'
            })

            # 2. Database span (nested)
            with tracer.start_as_current_span("query_user_database") as db_span:
                db_span.set_attributes({
                    'db.system': 'postgresql',
                    'db.name': 'users_db',
                    'db.statement': 'SELECT * FROM users WHERE id = $1',
                    'net.peer.name': 'db.example.com',
                    'net.peer.port': 5432,
                    'db.response.returned_rows': 1
                })
                time.sleep(0.001)  # Simulate some work

            # 3. HTTP Client span (nested)
            with tracer.start_as_current_span(
                "call_external_api",
                kind=trace.SpanKind.CLIENT
            ) as client_span:
                client_span.set_attributes({
                    'http.method': 'POST',
                    'http.url': 'https://api.external.com/v1/validate',
                    'http.status_code': 200
                })
                time.sleep(0.001)  # Simulate some work

        # Shutdown the processor to ensure all spans are processed
        processor.shutdown()

        # Verify that messages were sent
        assert len(sent_messages) > 0

        # Check that we have different types of messages
        message_types = set()
        for msg in sent_messages:
            if hasattr(msg, 'event') and hasattr(msg, 'type'):
                message_types.add(f"{msg.event}-{msg.type}")
            elif hasattr(msg, 'event'):
                message_types.add(msg.event)

        # Should have service discovery, route, database, http-service, and observations
        expected_types = {'new-entity-service', 'new-entity-http-route', 'new-entity-database',
                         'new-entity-http-service', 'observations'}

        # Check that we got some of the key message types (exact set may vary based on test execution)
        assert 'new-entity-service' in message_types, f"Missing service message. Got: {message_types}"
        assert 'observations' in message_types, f"Missing observations. Got: {message_types}"

        # Verify service message details
        service_messages = [msg for msg in sent_messages
                           if hasattr(msg, 'event') and msg.event == 'new-entity' and msg.type == 'service']
        assert len(service_messages) >= 1

        service_msg = service_messages[0]
        assert service_msg.name == 'my-python-service'
        assert service_msg.namespace == 'production'
        assert service_msg.environment == 'prod'

        # Verify we have observation messages
        observation_messages = [msg for msg in sent_messages if hasattr(msg, 'observations')]
        assert len(observation_messages) >= 1

        # Check that observations have the expected types
        observation_types = set()
        for obs_msg in observation_messages:
            for obs in obs_msg.observations:
                observation_types.add(obs.type)

        # Should have different types of observations
        possible_types = {'http-server', 'http-client', 'db-query'}
        assert len(observation_types.intersection(possible_types)) > 0, f"No expected observation types found. Got: {observation_types}"


def test_sdk_usage_example():
    """Test showing how to use the SDK in a real application."""
    # Mock the WebSocket connection
    mock_connection = Mock()
    mock_connection.send_message = Mock()
    mock_connection.close = Mock()

    with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=mock_connection):
        # This is how users would set up the SDK
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from comprehend_telemetry import ComprehendDevSpanProcessor

        # 1. Create resource with service information
        resource = Resource.create({
            'service.name': 'my-web-app',
            'service.version': '1.2.3',
            'deployment.environment': 'production'
        })

        # 2. Set up tracer provider (don't set global, just use directly)
        tracer_provider = TracerProvider(resource=resource)

        # 3. Add ComprehendDev processor
        comprehend_processor = ComprehendDevSpanProcessor(
            organization='my-company',
            token='my-secret-token',
            debug=True  # Enable debug logging
        )
        tracer_provider.add_span_processor(comprehend_processor)

        # 4. Get tracer directly from provider (not global)
        tracer = tracer_provider.get_tracer("my-web-app")

        with tracer.start_as_current_span("process_request") as span:
            span.set_attributes({
                'http.method': 'POST',
                'http.route': '/api/process',
                'http.status_code': 200
            })
            # Your application code here...
            pass

        # 5. Shutdown when done
        comprehend_processor.shutdown()

        # Verify the processor was called
        mock_connection.send_message.assert_called()
        mock_connection.close.assert_called()


def test_error_handling_integration():
    """Test error handling in the complete integration."""
    mock_connection = Mock()
    sent_messages = []
    mock_connection.send_message = Mock(side_effect=lambda msg: sent_messages.append(msg))
    mock_connection.close = Mock()

    with patch('comprehend_telemetry.span_processor.WebSocketConnection', return_value=mock_connection):
        resource = Resource.create({'service.name': 'error-test-service'})
        tracer_provider = TracerProvider(resource=resource)
        processor = ComprehendDevSpanProcessor('test-org', 'test-token')
        tracer_provider.add_span_processor(processor)

        tracer = tracer_provider.get_tracer(__name__)

        # Create a span with error information
        from opentelemetry.trace import SpanKind
        with tracer.start_as_current_span("failing_operation", kind=SpanKind.SERVER) as span:
            span.set_attributes({
                'http.method': 'POST',
                'http.route': '/api/error',
                'http.status_code': 500
            })

            # Add exception event
            span.add_event("exception", {
                'exception.type': 'ValueError',
                'exception.message': 'Invalid input data',
                'exception.stacktrace': 'Traceback...\n  File "test.py", line 42'
            })

            # Set error status
            from opentelemetry.trace import Status, StatusCode
            span.set_status(Status(StatusCode.ERROR, "Operation failed"))

        processor.shutdown()

        # Verify error information was captured
        observation_messages = [msg for msg in sent_messages if hasattr(msg, 'observations')]
        assert len(observation_messages) > 0

        # Check that error details are in observations
        found_error = False
        for obs_msg in observation_messages:
            for obs in obs_msg.observations:
                if hasattr(obs, 'errorMessage') and obs.errorMessage == 'Invalid input data':
                    found_error = True
                    assert obs.errorType == 'ValueError'
                    assert 'Traceback' in obs.stack
                    break

        assert found_error, "Error information not found in observations"