"""Wire protocol type definitions for comprehend.dev telemetry."""

from typing import Literal, Union, List, Optional, Any, Dict
from dataclasses import dataclass, asdict
import json

# Time representation: Python OpenTelemetry uses nanosecond integers
# TypeScript uses HrTime which is [seconds, nanoseconds]
# We'll use nanosecond integers and convert when serializing to match wire protocol
HrTime = int  # nanoseconds since epoch

# Utility functions for time conversion
def hrtime_to_tuple(ns_time: int) -> List[int]:
    """Convert nanosecond timestamp to [seconds, nanoseconds] tuple for wire protocol."""
    return [ns_time // 1_000_000_000, ns_time % 1_000_000_000]


def tuple_to_hrtime(time_tuple: List[int]) -> int:
    """Convert [seconds, nanoseconds] tuple to nanosecond timestamp."""
    return time_tuple[0] * 1_000_000_000 + time_tuple[1]


# Base message types
@dataclass
class InitMessage:
    """Initialize connection with token."""
    event: Literal["init"] = "init"
    protocolVersion: Literal[1] = 1
    token: str = ""


# Entity messages
@dataclass
class NewObservedServiceMessage:
    """New observed service entity."""
    event: Literal["new-entity"] = "new-entity"
    type: Literal["service"] = "service"
    hash: str = ""
    name: str = ""
    namespace: Optional[str] = None
    environment: Optional[str] = None


@dataclass
class NewObservedHttpRouteMessage:
    """New observed HTTP route entity."""
    event: Literal["new-entity"] = "new-entity"
    type: Literal["http-route"] = "http-route"
    hash: str = ""
    parent: str = ""
    method: str = ""
    route: str = ""


@dataclass
class NewObservedDatabaseMessage:
    """New observed database entity."""
    event: Literal["new-entity"] = "new-entity"
    type: Literal["database"] = "database"
    hash: str = ""
    system: str = ""
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None


@dataclass
class NewObservedHttpServiceMessage:
    """New observed HTTP service entity."""
    event: Literal["new-entity"] = "new-entity"
    type: Literal["http-service"] = "http-service"
    hash: str = ""
    protocol: str = ""
    host: str = ""
    port: int = 0


# Union type for all entity messages
NewObservedEntityMessage = Union[
    NewObservedServiceMessage,
    NewObservedHttpRouteMessage,
    NewObservedDatabaseMessage,
    NewObservedHttpServiceMessage
]


# Interaction messages
@dataclass
class NewObservedHttpRequestMessage:
    """New observed HTTP request interaction."""
    event: Literal["new-interaction"] = "new-interaction"
    type: Literal["http-request"] = "http-request"
    hash: str = ""
    from_: str = ""  # 'from' is a Python keyword
    to: str = ""


@dataclass
class NewObservedDatabaseConnectionMessage:
    """New observed database connection interaction."""
    event: Literal["new-interaction"] = "new-interaction"
    type: Literal["db-connection"] = "db-connection"
    hash: str = ""
    from_: str = ""  # 'from' is a Python keyword
    to: str = ""
    connection: Optional[str] = None
    user: Optional[str] = None


@dataclass
class NewObservedDatabaseQueryMessage:
    """New observed database query interaction."""
    event: Literal["new-interaction"] = "new-interaction"
    type: Literal["db-query"] = "db-query"
    hash: str = ""
    from_: str = ""  # 'from' is a Python keyword
    to: str = ""
    query: str = ""
    selects: Optional[List[str]] = None
    inserts: Optional[List[str]] = None
    updates: Optional[List[str]] = None
    deletes: Optional[List[str]] = None


# Union type for all interaction messages
NewObservedInteractionMessage = Union[
    NewObservedHttpRequestMessage,
    NewObservedDatabaseConnectionMessage,
    NewObservedDatabaseQueryMessage
]


# Observation types
@dataclass
class HttpClientObservation:
    """HTTP client observation."""
    type: Literal["http-client"] = "http-client"
    subject: str = ""  # Hash of the entity or interaction
    timestamp: HrTime = 0
    path: str = ""
    method: str = ""
    duration: HrTime = 0
    status: Optional[int] = None
    httpVersion: Optional[str] = None
    requestBytes: Optional[int] = None
    responseBytes: Optional[int] = None
    errorMessage: Optional[str] = None
    errorType: Optional[str] = None
    stack: Optional[str] = None


@dataclass
class HttpServerObservation:
    """HTTP server observation."""
    type: Literal["http-server"] = "http-server"
    subject: str = ""  # Hash of the entity or interaction
    timestamp: HrTime = 0
    path: str = ""
    status: int = 0
    duration: HrTime = 0
    httpVersion: Optional[str] = None
    requestBytes: Optional[int] = None
    responseBytes: Optional[int] = None
    userAgent: Optional[str] = None
    errorMessage: Optional[str] = None
    errorType: Optional[str] = None
    stack: Optional[str] = None


@dataclass
class DatabaseQueryObservation:
    """Database query observation."""
    type: Literal["db-query"] = "db-query"
    subject: str = ""  # Hash of the entity or interaction
    timestamp: HrTime = 0
    duration: HrTime = 0
    returnedRows: Optional[int] = None
    errorMessage: Optional[str] = None
    errorType: Optional[str] = None
    stack: Optional[str] = None


# Union type for all observations
Observation = Union[
    HttpClientObservation,
    HttpServerObservation,
    DatabaseQueryObservation
]


@dataclass
class ObservationMessage:
    """Message containing observations."""
    event: Literal["observations"] = "observations"
    seq: int = 0
    observations: List[Observation] = None

    def __post_init__(self):
        if self.observations is None:
            self.observations = []


# Response message types
@dataclass
class InitAck:
    """Acknowledgment of successful initialization."""
    type: Literal["ack-authorized"] = "ack-authorized"


@dataclass
class ObservedAck:
    """Acknowledgment of observed entity/interaction."""
    type: Literal["ack-observed"] = "ack-observed"
    hash: str = ""


@dataclass
class ObservationsAck:
    """Acknowledgment of observations batch."""
    type: Literal["ack-observations"] = "ack-observations"
    seq: int = 0


# Union types for message categories
ObservationInputMessage = Union[
    InitMessage,
    NewObservedEntityMessage,
    NewObservedInteractionMessage,
    ObservationMessage
]

ObservationOutputMessage = Union[
    InitAck,
    ObservedAck,
    ObservationsAck
]


# JSON serialization support
def _convert_for_wire_protocol(obj: Any) -> Any:
    """Recursively convert objects for wire protocol serialization."""
    if hasattr(obj, '__dataclass_fields__'):
        # Convert dataclass to dict field by field (not using asdict to avoid deep conversion)
        data = {}
        for field_name in obj.__dataclass_fields__.keys():
            field_value = getattr(obj, field_name)

            # Skip None values - optional fields should be omitted entirely
            if field_value is None:
                continue

            # Handle 'from_' field name conversion
            if field_name == 'from_':
                data['from'] = field_value
            # Convert HrTime fields to [seconds, nanoseconds] tuples
            elif field_name in ['timestamp', 'duration'] and isinstance(field_value, int):
                data[field_name] = hrtime_to_tuple(field_value)
            # Recursively handle lists
            elif isinstance(field_value, list):
                data[field_name] = [_convert_for_wire_protocol(item) for item in field_value]
            # Recursively handle nested dataclasses
            elif hasattr(field_value, '__dataclass_fields__'):
                data[field_name] = _convert_for_wire_protocol(field_value)
            else:
                data[field_name] = field_value

        return data
    elif isinstance(obj, list):
        return [_convert_for_wire_protocol(item) for item in obj]
    else:
        return obj


class WireProtocolEncoder(json.JSONEncoder):
    """Custom JSON encoder for wire protocol messages."""

    def default(self, obj: Any) -> Any:
        if hasattr(obj, '__dataclass_fields__'):
            return _convert_for_wire_protocol(obj)
        return super().default(obj)


def serialize_message(message: Union[ObservationInputMessage, ObservationOutputMessage]) -> str:
    """Serialize a wire protocol message to JSON."""
    return json.dumps(message, cls=WireProtocolEncoder, separators=(',', ':'))


def deserialize_message(json_data: str) -> Dict[str, Any]:
    """Deserialize JSON to dictionary (type reconstruction would require more complex logic)."""
    data = json.loads(json_data)

    # Convert 'from' field back to 'from_' if present
    if 'from' in data:
        data['from_'] = data.pop('from')

    # Convert time tuples back to nanoseconds if present
    for field_name in ['timestamp', 'duration']:
        if field_name in data and isinstance(data[field_name], list):
            data[field_name] = tuple_to_hrtime(data[field_name])

    return data