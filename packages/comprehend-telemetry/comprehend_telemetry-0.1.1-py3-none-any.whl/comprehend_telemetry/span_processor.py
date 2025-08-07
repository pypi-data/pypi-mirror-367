"""ComprehendDev span processor for OpenTelemetry Python SDK."""

import hashlib
from typing import Dict, List, Optional, Callable, Union, Set
from urllib.parse import urlparse
from dataclasses import dataclass

from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor
from opentelemetry.trace import Context, SpanKind, StatusCode

from .websocket_connection import WebSocketConnection
from .sql_analyzer import analyze_sql
from .wire_protocol import (
    NewObservedServiceMessage,
    NewObservedHttpRouteMessage,
    NewObservedDatabaseMessage,
    NewObservedHttpServiceMessage,
    NewObservedHttpRequestMessage,
    NewObservedDatabaseConnectionMessage,
    NewObservedDatabaseQueryMessage,
    ObservationMessage,
    HttpServerObservation,
    HttpClientObservation,
    DatabaseQueryObservation,
    ObservationInputMessage
)


# Data classes for tracking observed entities
@dataclass
class ObservedService:
    """Service that has been observed."""
    name: str
    namespace: Optional[str]
    environment: Optional[str]
    hash: str
    http_routes: List['ObservedHTTPRoute']


@dataclass
class ObservedHTTPRoute:
    """HTTP route that has been observed."""
    method: str
    route: str
    hash: str


@dataclass
class ObservedDatabase:
    """Database that has been observed."""
    system: str
    connection: Optional[str]  # Connection string, scrubbed of user info
    host: Optional[str]
    port: Optional[int]
    name: Optional[str]
    hash: str


@dataclass
class ObservedHttpService:
    """HTTP service that has been observed."""
    protocol: str
    host: str
    port: Optional[int]
    hash: str


@dataclass
class ObservedHttpRequest:
    """HTTP request interaction that has been observed."""
    hash: str


@dataclass
class ObservedDatabaseConnection:
    """Database connection interaction that has been observed."""
    hash: str
    connection: Optional[str]
    user: Optional[str]


@dataclass
class ObservedDatabaseQuery:
    """Database query interaction that has been observed."""
    hash: str
    query: str


# Set of SQL database systems
SQL_DB_SYSTEMS: Set[str] = {
    'mysql', 'postgresql', 'mssql', 'oracle', 'db2', 'sqlite', 'hsqldb', 'h2',
    'informix', 'cockroachdb', 'redshift', 'tidb', 'trino', 'greenplum'
}


def hash_id_string(id_string: str) -> str:
    """Create hash from ID string."""
    return hashlib.sha256(id_string.encode('utf-8')).hexdigest()


def parse_database_connection_string(conn: str) -> Dict[str, Optional[str]]:
    """Parse database connection string and scrub sensitive info."""
    try:
        # Try URL-style parsing first
        parsed = urlparse(conn)
        if parsed.scheme:
            user = parsed.username
            host = parsed.hostname
            port = str(parsed.port) if parsed.port else None
            db_name = parsed.path.lstrip('/') if parsed.path else None

            # Create scrubbed URL
            scrubbed_url = f"{parsed.scheme}://{host}"
            if port:
                scrubbed_url += f":{port}"
            if db_name:
                scrubbed_url += f"/{db_name}"
            if parsed.query:
                scrubbed_url += f"?{parsed.query}"

            return {
                'scrubbed': scrubbed_url,
                'user': user,
                'host': host,
                'port': port,
                'name': db_name
            }
    except Exception:
        pass

    # Not a URL-style string; try semi-structured parsing
    parts = conn.split(';')
    kv: Dict[str, str] = {}

    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            kv[k.strip().lower()] = v.strip()

    user = kv.get('user id') or kv.get('uid')
    host = kv.get('server') or kv.get('data source') or kv.get('address')
    port = kv.get('port')
    name = kv.get('database') or kv.get('initial catalog')

    # Reconstruct scrubbed connection string without credentials
    scrubbed_parts = []
    for k, v in kv.items():
        if k not in ['user id', 'uid', 'password', 'pwd']:
            scrubbed_parts.append(f"{k}={v}")
    scrubbed = ';'.join(scrubbed_parts)

    return {
        'scrubbed': scrubbed,
        'user': user,
        'host': host,
        'port': port,
        'name': name
    }


def extract_error_info(span: ReadableSpan) -> Dict[str, Optional[str]]:
    """Extract error information from span."""
    # Try to extract from structured 'exception' event first
    for event in span.events:
        if event.name == 'exception' and event.attributes:
            message = event.attributes.get('exception.message')
            error_type = event.attributes.get('exception.type')
            stack = event.attributes.get('exception.stacktrace')
            if message or error_type or stack:
                return {
                    'message': str(message) if message else None,
                    'type': str(error_type) if error_type else None,
                    'stack': str(stack) if stack else None
                }

    # Fallback to attributes directly on the span
    attrs = span.attributes
    is_error = span.status.status_code == StatusCode.ERROR

    message = (
        attrs.get('exception.message') or
        attrs.get('http.error_message') or
        attrs.get('db.response.status_code') or
        (span.status.description if is_error else None)
    )

    error_type = (
        attrs.get('exception.type') or
        attrs.get('error.type') or
        attrs.get('http.error_name')
    )

    stack = attrs.get('exception.stacktrace')

    return {
        'message': str(message) if message else None,
        'type': str(error_type) if error_type else None,
        'stack': str(stack) if stack else None
    }


def get_tables_with_operation(table_ops: Dict[str, List[str]], operation: str) -> Optional[List[str]]:
    """Get tables that have a specific operation."""
    op = operation.upper()
    result = [table for table, ops in table_ops.items() if op in ops]
    return result if result else None


class ComprehendDevSpanProcessor(SpanProcessor):
    """Span processor that sends telemetry data to comprehend.dev."""

    def __init__(
        self,
        organization: str,
        token: str,
        debug: Union[bool, Callable[[str], None], None] = None
    ):
        """Initialize the span processor.

        Args:
            organization: Organization name for comprehend.dev
            token: API token for authentication
            debug: Debug logging - True for console logging, callable for custom logging, False/None to disable
        """
        # Set up debug logger
        if debug is True:
            logger = print
        elif callable(debug):
            logger = debug
        else:
            logger = None

        self.connection = WebSocketConnection(organization, token, logger)
        self.observed_services: List[ObservedService] = []
        self.observed_databases: List[ObservedDatabase] = []
        self.observed_http_services: List[ObservedHttpService] = []
        self.observed_interactions: Dict[str, Dict[str, Dict[str, Union[
            List[ObservedDatabaseConnection],
            List[ObservedDatabaseQuery],
            Optional[ObservedHttpRequest]
        ]]]] = {}
        self.observations_seq = 1

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Called when a span is started (no-op for this processor)."""
        pass

    def on_end(self, span: ReadableSpan) -> None:
        """Process a span when it ends."""
        current_service = self._discover_service(span)
        if not current_service:
            return

        attrs = span.attributes

        # Process server spans (HTTP routes)
        if span.kind == SpanKind.SERVER:
            if attrs.get('http.route') and attrs.get('http.method'):
                self._process_http_route(
                    current_service,
                    str(attrs['http.route']),
                    str(attrs['http.method']),
                    span
                )

        # Process client spans (HTTP requests)
        elif span.kind == SpanKind.CLIENT:
            if attrs.get('http.url'):
                self._process_http_request(
                    current_service,
                    str(attrs['http.url']),
                    span
                )

        # Process database operations
        if attrs.get('db.system'):
            self._process_database_operation(current_service, span)

    def _discover_service(self, span: ReadableSpan) -> Optional[ObservedService]:
        """Discover and register a service from span resource attributes."""
        res_attrs = span.resource.attributes
        name = res_attrs.get('service.name')
        if not name:
            return None

        name = str(name)
        namespace = str(res_attrs['service.namespace']) if res_attrs.get('service.namespace') else None
        environment = str(res_attrs['deployment.environment']) if res_attrs.get('deployment.environment') else None

        # Look for existing service
        for existing in self.observed_services:
            if (existing.name == name and
                existing.namespace == namespace and
                existing.environment == environment):
                return existing

        # Create new service
        id_string = f"service:{name}:{namespace or ''}:{environment or ''}"
        hash_val = hash_id_string(id_string)
        new_service = ObservedService(
            name=name,
            namespace=namespace,
            environment=environment,
            hash=hash_val,
            http_routes=[]
        )
        self.observed_services.append(new_service)

        # Send service message
        message = NewObservedServiceMessage(
            event='new-entity',
            type='service',
            hash=hash_val,
            name=name
        )
        if namespace:
            message.namespace = namespace
        if environment:
            message.environment = environment

        self._ingest_message(message)
        return new_service

    def _process_http_route(
        self,
        service: ObservedService,
        route: str,
        method: str,
        span: ReadableSpan
    ) -> None:
        """Process HTTP server span and create route entities."""
        # Check if route already exists
        observed_route = None
        for r in service.http_routes:
            if r.route == route and r.method == method:
                observed_route = r
                break

        if not observed_route:
            # Create new route
            id_string = f"http-route:{service.hash}:{method}:{route}"
            hash_val = hash_id_string(id_string)
            observed_route = ObservedHTTPRoute(
                method=method,
                route=route,
                hash=hash_val
            )
            service.http_routes.append(observed_route)

            # Send route message
            message = NewObservedHttpRouteMessage(
                event='new-entity',
                type='http-route',
                hash=hash_val,
                parent=service.hash,
                method=method,
                route=route
            )
            self._ingest_message(message)

        # Extract request path
        attrs = span.attributes
        path = '/'

        if attrs.get('http.target'):
            try:
                target = str(attrs['http.target'])
                # This might be just a path like "/search?q=foo"
                # Use placeholder base for relative URLs
                from urllib.parse import urljoin
                full_url = urljoin('http://placeholder', target)
                parsed = urlparse(full_url)
                path = parsed.path
            except Exception:
                path = '/'
        elif attrs.get('http.url'):
            try:
                url = str(attrs['http.url'])
                parsed = urlparse(url)
                path = parsed.path or '/'
            except Exception:
                path = '/'

        # Build observation
        status = int(attrs.get('http.status_code', 0))
        duration_ns = span.end_time - span.start_time if span.end_time else 0
        http_version = str(attrs['http.flavor']) if attrs.get('http.flavor') else None
        user_agent = str(attrs['http.user_agent']) if attrs.get('http.user_agent') else None
        request_bytes = int(attrs['http.request_content_length']) if attrs.get('http.request_content_length') else None
        response_bytes = int(attrs['http.response_content_length']) if attrs.get('http.response_content_length') else None

        error_info = extract_error_info(span)

        observation = HttpServerObservation(
            type='http-server',
            subject=observed_route.hash,
            timestamp=span.start_time,
            path=path,
            status=status,
            duration=duration_ns
        )

        # Add optional fields
        if http_version:
            observation.httpVersion = http_version
        if user_agent:
            observation.userAgent = user_agent
        if request_bytes is not None:
            observation.requestBytes = request_bytes
        if response_bytes is not None:
            observation.responseBytes = response_bytes
        if error_info['message']:
            observation.errorMessage = error_info['message']
        if error_info['type']:
            observation.errorType = error_info['type']
        if error_info['stack']:
            observation.stack = error_info['stack']

        self._ingest_message(ObservationMessage(
            event='observations',
            seq=self.observations_seq,
            observations=[observation]
        ))
        self.observations_seq += 1

    def _process_http_request(
        self,
        current_service: ObservedService,
        url: str,
        span: ReadableSpan
    ) -> None:
        """Process HTTP client span and create service entities and interactions."""
        try:
            parsed = urlparse(url)
            protocol = parsed.scheme
            host = parsed.hostname
            port = parsed.port

            if not host:
                return

            if port is None:
                port = 443 if protocol == 'https' else 80

        except Exception:
            return

        # Find or create HTTP service
        http_service = None
        for service in self.observed_http_services:
            if (service.protocol == protocol and
                service.host == host and
                service.port == port):
                http_service = service
                break

        if not http_service:
            id_string = f"http-service:{protocol}:{host}:{port}"
            hash_val = hash_id_string(id_string)
            http_service = ObservedHttpService(
                protocol=protocol,
                host=host,
                port=port,
                hash=hash_val
            )
            self.observed_http_services.append(http_service)

            # Send HTTP service message
            message = NewObservedHttpServiceMessage(
                event='new-entity',
                type='http-service',
                hash=hash_val,
                protocol=protocol,
                host=host,
                port=port
            )
            self._ingest_message(message)

        # Create HTTP request interaction
        interactions = self._get_interactions(current_service.hash, http_service.hash)
        if not interactions.get('httpRequest'):
            id_string = f"http-request:{current_service.hash}:{http_service.hash}"
            hash_val = hash_id_string(id_string)
            http_request = ObservedHttpRequest(hash=hash_val)
            interactions['httpRequest'] = http_request

            message = NewObservedHttpRequestMessage(
                event='new-interaction',
                type='http-request',
                hash=hash_val,
                from_=current_service.hash,
                to=http_service.hash
            )
            self._ingest_message(message)

        # Build observation
        attrs = span.attributes
        path = parsed.path or '/'
        method = str(attrs.get('http.method', ''))
        if not method:
            return

        status = int(attrs['http.status_code']) if attrs.get('http.status_code') else None
        duration_ns = span.end_time - span.start_time if span.end_time else 0
        http_version = str(attrs['http.flavor']) if attrs.get('http.flavor') else None
        request_bytes = int(attrs['http.request_content_length']) if attrs.get('http.request_content_length') else None
        response_bytes = int(attrs['http.response_content_length']) if attrs.get('http.response_content_length') else None

        error_info = extract_error_info(span)

        observation = HttpClientObservation(
            type='http-client',
            subject=interactions['httpRequest'].hash,
            timestamp=span.start_time,
            path=path,
            method=method,
            duration=duration_ns
        )

        # Add optional fields
        if status is not None:
            observation.status = status
        if http_version:
            observation.httpVersion = http_version
        if request_bytes is not None:
            observation.requestBytes = request_bytes
        if response_bytes is not None:
            observation.responseBytes = response_bytes
        if error_info['message']:
            observation.errorMessage = error_info['message']
        if error_info['type']:
            observation.errorType = error_info['type']
        if error_info['stack']:
            observation.stack = error_info['stack']

        self._ingest_message(ObservationMessage(
            event='observations',
            seq=self.observations_seq,
            observations=[observation]
        ))
        self.observations_seq += 1

    def _process_database_operation(
        self,
        current_service: ObservedService,
        span: ReadableSpan
    ) -> None:
        """Process database operation span."""
        attrs = span.attributes
        system = str(attrs['db.system'])

        # Parse connection string
        raw_connection = str(attrs['db.connection_string']) if attrs.get('db.connection_string') else None
        if raw_connection:
            parsed = parse_database_connection_string(raw_connection)
        else:
            host_attr = attrs.get('net.peer.name') or attrs.get('net.peer.ip')
            port_attr = attrs.get('net.peer.port')
            name_attr = attrs.get('db.name')

            parsed = {
                'scrubbed': '',
                'user': None,
                'host': str(host_attr) if host_attr else None,
                'port': str(port_attr) if port_attr else None,
                'name': str(name_attr) if name_attr else None
            }

        # Find or create database
        port_str = str(parsed['port']) if parsed['port'] else ''
        db_hash = hash_id_string(f"database:{system}:{parsed['host'] or ''}:{port_str}:{parsed['name'] or ''}")
        observed_database = None
        for db in self.observed_databases:
            if db.hash == db_hash:
                observed_database = db
                break

        if not observed_database:
            observed_database = ObservedDatabase(
                system=system,
                host=parsed['host'],
                port=int(parsed['port']) if parsed['port'] else None,
                name=parsed['name'],
                hash=db_hash,
                connection=parsed['scrubbed']
            )
            self.observed_databases.append(observed_database)

            # Send database message
            message = NewObservedDatabaseMessage(
                event='new-entity',
                type='database',
                hash=db_hash,
                system=system
            )
            if parsed['name']:
                message.name = parsed['name']
            if parsed['host']:
                message.host = parsed['host']
            if parsed['port']:
                message.port = int(parsed['port'])

            self._ingest_message(message)

        # Create database connection interaction
        interactions = self._get_interactions(current_service.hash, observed_database.hash)
        db_connections = interactions.setdefault('dbConnections', [])

        connection_interaction = None
        for conn in db_connections:
            if (conn.connection == parsed['scrubbed'] and
                conn.user == parsed['user']):
                connection_interaction = conn
                break

        if not connection_interaction:
            conn_hash = hash_id_string(f"db-connection:{current_service.hash}:{observed_database.hash}:{parsed['scrubbed'] or ''}:{parsed['user'] or ''}")
            connection_interaction = ObservedDatabaseConnection(
                hash=conn_hash,
                connection=parsed['scrubbed'],
                user=parsed['user']
            )
            db_connections.append(connection_interaction)

            message = NewObservedDatabaseConnectionMessage(
                event='new-interaction',
                type='db-connection',
                hash=conn_hash,
                from_=current_service.hash,
                to=observed_database.hash
            )
            if parsed['scrubbed']:
                message.connection = parsed['scrubbed']
            if parsed['user']:
                message.user = parsed['user']

            self._ingest_message(message)

        # Process SQL query if applicable
        if system in SQL_DB_SYSTEMS and attrs.get('db.statement'):
            statement = str(attrs['db.statement'])
            query_info = analyze_sql(statement)

            db_queries = interactions.setdefault('dbQueries', [])
            query_interaction = None
            for query in db_queries:
                if query.query == query_info.normalized_query:
                    query_interaction = query
                    break

            if not query_interaction:
                query_hash = hash_id_string(f"db-query:{current_service.hash}:{observed_database.hash}:{query_info.normalized_query}")
                query_interaction = ObservedDatabaseQuery(
                    hash=query_hash,
                    query=query_info.normalized_query
                )
                db_queries.append(query_interaction)

                # Extract table operations
                table_ops = query_info.table_operations
                selects = get_tables_with_operation(table_ops, 'SELECT')
                inserts = get_tables_with_operation(table_ops, 'INSERT')
                updates = get_tables_with_operation(table_ops, 'UPDATE')
                deletes = get_tables_with_operation(table_ops, 'DELETE')

                message = NewObservedDatabaseQueryMessage(
                    event='new-interaction',
                    type='db-query',
                    hash=query_hash,
                    from_=current_service.hash,
                    to=observed_database.hash,
                    query=query_info.presentable_query
                )
                if selects:
                    message.selects = selects
                if inserts:
                    message.inserts = inserts
                if updates:
                    message.updates = updates
                if deletes:
                    message.deletes = deletes

                self._ingest_message(message)

            # Build observation
            duration_ns = span.end_time - span.start_time if span.end_time else 0
            returned_rows = (
                int(attrs['db.response.returned_rows']) if attrs.get('db.response.returned_rows') else
                int(attrs['db.sql.rows']) if attrs.get('db.sql.rows') else None
            )

            error_info = extract_error_info(span)

            observation = DatabaseQueryObservation(
                type='db-query',
                subject=query_interaction.hash,
                timestamp=span.start_time,
                duration=duration_ns
            )

            if returned_rows is not None:
                observation.returnedRows = returned_rows
            if error_info['message']:
                observation.errorMessage = error_info['message']
            if error_info['type']:
                observation.errorType = error_info['type']
            if error_info['stack']:
                observation.stack = error_info['stack']

            self._ingest_message(ObservationMessage(
                event='observations',
                seq=self.observations_seq,
                observations=[observation]
            ))
            self.observations_seq += 1

    def _get_interactions(self, from_hash: str, to_hash: str) -> Dict[str, Union[List, Optional[ObservedHttpRequest]]]:
        """Get or create interaction storage for a from->to relationship."""
        from_map = self.observed_interactions.setdefault(from_hash, {})
        interactions = from_map.setdefault(to_hash, {
            'httpRequest': None,
            'dbConnections': [],
            'dbQueries': []
        })
        return interactions

    def _ingest_message(self, message: ObservationInputMessage) -> None:
        """Send message through WebSocket connection."""
        self.connection.send_message(message)

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered data (no-op for this processor)."""
        return True

    def shutdown(self) -> bool:
        """Shutdown the processor and close connections."""
        self.connection.close()
        return True