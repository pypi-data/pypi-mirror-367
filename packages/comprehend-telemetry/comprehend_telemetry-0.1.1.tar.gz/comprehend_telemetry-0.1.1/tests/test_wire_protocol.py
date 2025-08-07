"""Tests for wire protocol type definitions."""

import json
import time
from comprehend_telemetry.wire_protocol import (
    # Time utilities
    hrtime_to_tuple, tuple_to_hrtime,

    # Message types
    InitMessage,
    NewObservedServiceMessage,
    NewObservedHttpRouteMessage,
    NewObservedDatabaseMessage,
    NewObservedHttpServiceMessage,
    NewObservedHttpRequestMessage,
    NewObservedDatabaseConnectionMessage,
    NewObservedDatabaseQueryMessage,
    HttpClientObservation,
    HttpServerObservation,
    DatabaseQueryObservation,
    ObservationMessage,
    InitAck,
    ObservedAck,
    ObservationsAck,

    # Serialization
    serialize_message,
    deserialize_message,
    WireProtocolEncoder
)


class TestTimeUtilities:
    """Test time conversion utilities."""

    def test_hrtime_conversion_roundtrip(self):
        """Test converting between nanoseconds and [seconds, nanoseconds] tuple."""
        ns_time = 1754411344309532945

        # Convert to tuple
        time_tuple = hrtime_to_tuple(ns_time)
        assert time_tuple == [1754411344, 309532945]

        # Convert back
        converted_back = tuple_to_hrtime(time_tuple)
        assert converted_back == ns_time

    def test_hrtime_zero(self):
        """Test time conversion with zero."""
        assert hrtime_to_tuple(0) == [0, 0]
        assert tuple_to_hrtime([0, 0]) == 0

    def test_hrtime_large_values(self):
        """Test time conversion with large values."""
        # Very large timestamp
        large_ns = 9999999999999999999
        tuple_form = hrtime_to_tuple(large_ns)
        assert tuple_to_hrtime(tuple_form) == large_ns


class TestMessageTypes:
    """Test wire protocol message type definitions."""

    def test_init_message(self):
        """Test InitMessage structure."""
        msg = InitMessage(token="test-token")
        assert msg.event == "init"
        assert msg.protocolVersion == 1
        assert msg.token == "test-token"

    def test_service_message(self):
        """Test NewObservedServiceMessage structure."""
        msg = NewObservedServiceMessage(
            hash="service-hash",
            name="my-service",
            namespace="prod",
            environment="production"
        )
        assert msg.event == "new-entity"
        assert msg.type == "service"
        assert msg.hash == "service-hash"
        assert msg.name == "my-service"
        assert msg.namespace == "prod"
        assert msg.environment == "production"

    def test_http_route_message(self):
        """Test NewObservedHttpRouteMessage structure."""
        msg = NewObservedHttpRouteMessage(
            hash="route-hash",
            parent="service-hash",
            method="GET",
            route="/api/users/{id}"
        )
        assert msg.event == "new-entity"
        assert msg.type == "http-route"
        assert msg.hash == "route-hash"
        assert msg.parent == "service-hash"
        assert msg.method == "GET"
        assert msg.route == "/api/users/{id}"

    def test_database_message(self):
        """Test NewObservedDatabaseMessage structure."""
        msg = NewObservedDatabaseMessage(
            hash="db-hash",
            system="postgresql",
            name="mydb",
            host="localhost",
            port=5432
        )
        assert msg.event == "new-entity"
        assert msg.type == "database"
        assert msg.hash == "db-hash"
        assert msg.system == "postgresql"
        assert msg.name == "mydb"
        assert msg.host == "localhost"
        assert msg.port == 5432

    def test_http_service_message(self):
        """Test NewObservedHttpServiceMessage structure."""
        msg = NewObservedHttpServiceMessage(
            hash="http-service-hash",
            protocol="https",
            host="api.example.com",
            port=443
        )
        assert msg.event == "new-entity"
        assert msg.type == "http-service"
        assert msg.hash == "http-service-hash"
        assert msg.protocol == "https"
        assert msg.host == "api.example.com"
        assert msg.port == 443

    def test_http_request_interaction(self):
        """Test NewObservedHttpRequestMessage structure."""
        msg = NewObservedHttpRequestMessage(
            hash="request-hash",
            from_="client-hash",
            to="server-hash"
        )
        assert msg.event == "new-interaction"
        assert msg.type == "http-request"
        assert msg.hash == "request-hash"
        assert msg.from_ == "client-hash"
        assert msg.to == "server-hash"

    def test_database_connection_interaction(self):
        """Test NewObservedDatabaseConnectionMessage structure."""
        msg = NewObservedDatabaseConnectionMessage(
            hash="conn-hash",
            from_="service-hash",
            to="db-hash",
            connection="connection-1",
            user="dbuser"
        )
        assert msg.event == "new-interaction"
        assert msg.type == "db-connection"
        assert msg.hash == "conn-hash"
        assert msg.from_ == "service-hash"
        assert msg.to == "db-hash"
        assert msg.connection == "connection-1"
        assert msg.user == "dbuser"

    def test_database_query_interaction(self):
        """Test NewObservedDatabaseQueryMessage structure."""
        msg = NewObservedDatabaseQueryMessage(
            hash="query-hash",
            from_="service-hash",
            to="db-hash",
            query="SELECT * FROM users",
            selects=["users"],
            inserts=None,
            updates=None,
            deletes=None
        )
        assert msg.event == "new-interaction"
        assert msg.type == "db-query"
        assert msg.hash == "query-hash"
        assert msg.from_ == "service-hash"
        assert msg.to == "db-hash"
        assert msg.query == "SELECT * FROM users"
        assert msg.selects == ["users"]
        assert msg.inserts is None


class TestObservations:
    """Test observation message types."""

    def test_http_client_observation(self):
        """Test HttpClientObservation structure."""
        obs = HttpClientObservation(
            subject="request-hash",
            timestamp=1754411344309532945,
            path="/api/users",
            method="GET",
            duration=150000000,  # 150ms in nanoseconds
            status=200,
            httpVersion="1.1",
            requestBytes=100,
            responseBytes=500
        )
        assert obs.type == "http-client"
        assert obs.subject == "request-hash"
        assert obs.timestamp == 1754411344309532945
        assert obs.path == "/api/users"
        assert obs.method == "GET"
        assert obs.duration == 150000000
        assert obs.status == 200
        assert obs.httpVersion == "1.1"
        assert obs.requestBytes == 100
        assert obs.responseBytes == 500

    def test_http_server_observation(self):
        """Test HttpServerObservation structure."""
        obs = HttpServerObservation(
            subject="route-hash",
            timestamp=1754411344309532945,
            path="/api/users",
            status=200,
            duration=50000000,  # 50ms in nanoseconds
            userAgent="Mozilla/5.0"
        )
        assert obs.type == "http-server"
        assert obs.subject == "route-hash"
        assert obs.timestamp == 1754411344309532945
        assert obs.path == "/api/users"
        assert obs.status == 200
        assert obs.duration == 50000000
        assert obs.userAgent == "Mozilla/5.0"

    def test_database_query_observation(self):
        """Test DatabaseQueryObservation structure."""
        obs = DatabaseQueryObservation(
            subject="query-hash",
            timestamp=1754411344309532945,
            duration=25000000,  # 25ms in nanoseconds
            returnedRows=10
        )
        assert obs.type == "db-query"
        assert obs.subject == "query-hash"
        assert obs.timestamp == 1754411344309532945
        assert obs.duration == 25000000
        assert obs.returnedRows == 10

    def test_observation_message(self):
        """Test ObservationMessage structure."""
        obs1 = HttpClientObservation(subject="hash1", timestamp=123, path="/test", method="GET", duration=100)
        obs2 = DatabaseQueryObservation(subject="hash2", timestamp=456, duration=200)

        msg = ObservationMessage(seq=1, observations=[obs1, obs2])
        assert msg.event == "observations"
        assert msg.seq == 1
        assert len(msg.observations) == 2
        assert msg.observations[0] == obs1
        assert msg.observations[1] == obs2

    def test_observation_message_default_list(self):
        """Test ObservationMessage initializes empty list by default."""
        msg = ObservationMessage(seq=1)
        assert msg.observations == []


class TestResponseMessages:
    """Test response message types."""

    def test_init_ack(self):
        """Test InitAck structure."""
        ack = InitAck()
        assert ack.type == "ack-authorized"

    def test_observed_ack(self):
        """Test ObservedAck structure."""
        ack = ObservedAck(hash="test-hash")
        assert ack.type == "ack-observed"
        assert ack.hash == "test-hash"

    def test_observations_ack(self):
        """Test ObservationsAck structure."""
        ack = ObservationsAck(seq=5)
        assert ack.type == "ack-observations"
        assert ack.seq == 5


class TestSerialization:
    """Test JSON serialization and deserialization."""

    def test_serialize_init_message(self):
        """Test serializing InitMessage."""
        msg = InitMessage(token="secret-token")
        json_str = serialize_message(msg)

        # Parse to verify structure
        data = json.loads(json_str)
        assert data["event"] == "init"
        assert data["protocolVersion"] == 1
        assert data["token"] == "secret-token"

    def test_serialize_service_message(self):
        """Test serializing service message."""
        msg = NewObservedServiceMessage(
            hash="srv-hash",
            name="api-service",
            namespace="prod"
        )
        json_str = serialize_message(msg)

        data = json.loads(json_str)
        assert data["event"] == "new-entity"
        assert data["type"] == "service"
        assert data["hash"] == "srv-hash"
        assert data["name"] == "api-service"
        assert data["namespace"] == "prod"

    def test_serialize_interaction_with_from_field(self):
        """Test serializing interaction message with 'from' field conversion."""
        msg = NewObservedHttpRequestMessage(
            hash="req-hash",
            from_="client-hash",
            to="server-hash"
        )
        json_str = serialize_message(msg)

        data = json.loads(json_str)
        assert data["event"] == "new-interaction"
        assert data["type"] == "http-request"
        assert data["hash"] == "req-hash"
        assert data["from"] == "client-hash"  # from_ -> from
        assert data["to"] == "server-hash"
        assert "from_" not in data  # Should not have the Python field name

    def test_serialize_observation_with_time_conversion(self):
        """Test serializing observation with time field conversion."""
        obs = HttpClientObservation(
            subject="req-hash",
            timestamp=1754411344309532945,  # nanoseconds
            path="/api/test",
            method="POST",
            duration=150000000  # 150ms in nanoseconds
        )

        msg = ObservationMessage(seq=1, observations=[obs])
        json_str = serialize_message(msg)

        data = json.loads(json_str)
        assert data["event"] == "observations"
        assert data["seq"] == 1
        assert len(data["observations"]) == 1

        obs_data = data["observations"][0]
        assert obs_data["type"] == "http-client"
        assert obs_data["subject"] == "req-hash"
        assert obs_data["path"] == "/api/test"
        assert obs_data["method"] == "POST"

        # Check time conversion to [seconds, nanoseconds]
        assert obs_data["timestamp"] == [1754411344, 309532945]
        assert obs_data["duration"] == [0, 150000000]

    def test_deserialize_message(self):
        """Test deserializing JSON back to dictionary."""
        json_data = '{"event":"new-interaction","type":"http-request","hash":"req-hash","from":"client","to":"server"}'

        data = deserialize_message(json_data)
        assert data["event"] == "new-interaction"
        assert data["type"] == "http-request"
        assert data["hash"] == "req-hash"
        assert data["from_"] == "client"  # from -> from_
        assert data["to"] == "server"
        assert "from" not in data

    def test_deserialize_with_time_conversion(self):
        """Test deserializing with time tuple conversion."""
        json_data = '{"type":"http-client","timestamp":[1754411344,309532945],"duration":[0,150000000]}'

        data = deserialize_message(json_data)
        assert data["type"] == "http-client"
        assert data["timestamp"] == 1754411344309532945  # Converted back to nanoseconds
        assert data["duration"] == 150000000

    def test_json_encoder_direct(self):
        """Test WireProtocolEncoder directly."""
        obs = DatabaseQueryObservation(
            subject="query-hash",
            timestamp=1000000000123456789,
            duration=50000000
        )

        encoder = WireProtocolEncoder()
        result = encoder.default(obs)

        assert result["type"] == "db-query"
        assert result["subject"] == "query-hash"
        assert result["timestamp"] == [1000000000, 123456789]
        assert result["duration"] == [0, 50000000]

    def test_serialization_roundtrip_compatibility(self):
        """Test that serialized format matches expected wire protocol format."""
        # Create a complex message similar to what would be sent
        query_obs = DatabaseQueryObservation(
            subject="query-abc123",
            timestamp=1754411344309532945,
            duration=25000000,
            returnedRows=5,
            errorMessage=None
        )

        msg = ObservationMessage(seq=42, observations=[query_obs])
        json_str = serialize_message(msg)

        # Verify it's compact JSON (no extra spaces)
        assert " " not in json_str or json_str.count(" ") == 0

        # Verify structure matches expected wire protocol
        data = json.loads(json_str)
        expected_structure = {
            "event": "observations",
            "seq": 42,
            "observations": [{
                "type": "db-query",
                "subject": "query-abc123",
                "timestamp": [1754411344, 309532945],
                "duration": [0, 25000000],
                "returnedRows": 5
                # Note: errorMessage is None so it should be omitted entirely
            }]
        }

        assert data == expected_structure

    def test_none_fields_omitted_across_all_types(self):
        """Test that None values are omitted for all message types with optional fields."""
        # Test service message
        service_msg = NewObservedServiceMessage(
            hash="srv-hash",
            name="my-service",
            namespace=None,  # Should be omitted
            environment="prod"
        )
        service_json = serialize_message(service_msg)
        service_data = json.loads(service_json)
        assert "namespace" not in service_data
        assert service_data["environment"] == "prod"

        # Test database message
        db_msg = NewObservedDatabaseMessage(
            hash="db-hash",
            system="postgresql",
            name=None,  # Should be omitted
            host="localhost",
            port=None   # Should be omitted
        )
        db_json = serialize_message(db_msg)
        db_data = json.loads(db_json)
        assert "name" not in db_data
        assert "port" not in db_data
        assert db_data["host"] == "localhost"

        # Test database connection interaction
        conn_msg = NewObservedDatabaseConnectionMessage(
            hash="conn-hash",
            from_="service-hash",
            to="db-hash",
            connection=None,  # Should be omitted
            user="dbuser"
        )
        conn_json = serialize_message(conn_msg)
        conn_data = json.loads(conn_json)
        assert "connection" not in conn_data
        assert conn_data["user"] == "dbuser"

        # Test database query interaction
        query_msg = NewObservedDatabaseQueryMessage(
            hash="query-hash",
            from_="service-hash",
            to="db-hash",
            query="SELECT * FROM users",
            selects=["users"],
            inserts=None,   # Should be omitted
            updates=None,   # Should be omitted
            deletes=None    # Should be omitted
        )
        query_json = serialize_message(query_msg)
        query_data = json.loads(query_json)
        assert "inserts" not in query_data
        assert "updates" not in query_data
        assert "deletes" not in query_data
        assert query_data["selects"] == ["users"]

        # Test HTTP client observation
        http_obs = HttpClientObservation(
            subject="req-hash",
            timestamp=1000,
            path="/api/test",
            method="GET",
            duration=100,
            status=200,
            httpVersion=None,      # Should be omitted
            requestBytes=None,     # Should be omitted
            responseBytes=1024,
            errorMessage=None,     # Should be omitted
            errorType=None,        # Should be omitted
            stack=None            # Should be omitted
        )
        obs_msg = ObservationMessage(seq=1, observations=[http_obs])
        obs_json = serialize_message(obs_msg)
        obs_data = json.loads(obs_json)
        http_data = obs_data["observations"][0]

        assert "httpVersion" not in http_data
        assert "requestBytes" not in http_data
        assert "errorMessage" not in http_data
        assert "errorType" not in http_data
        assert "stack" not in http_data
        assert http_data["responseBytes"] == 1024
        assert http_data["status"] == 200