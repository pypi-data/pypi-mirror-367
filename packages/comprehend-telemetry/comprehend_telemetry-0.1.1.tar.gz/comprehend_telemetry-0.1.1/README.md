# comprehend-telemetry

OpenTelemetry integration for [comprehend.dev](https://comprehend.dev) - automatically capture and analyze your Python application's architecture and performance.

## Installation

```bash
pip install comprehend-telemetry
```

## Quick Start

Add the ComprehendDevSpanProcessor to your existing OpenTelemetry setup:

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from comprehend_telemetry import ComprehendDevSpanProcessor

# Set up OpenTelemetry with your service information
resource = Resource.create({
    "service.name": "my-python-service",
    "service.namespace": "production",
    "deployment.environment": "prod"
})

tracer_provider = TracerProvider(resource=resource)

# Add comprehend.dev telemetry processor
if os.getenv("COMPREHEND_OBSERVATIONS_TOKEN"):
    comprehend_processor = ComprehendDevSpanProcessor(
        organization='comprehend',  # Use your organization name
        token=os.getenv("COMPREHEND_OBSERVATIONS_TOKEN"),
        debug=True  # Optional: enable debug logging
    )
    tracer_provider.add_span_processor(comprehend_processor)

# Set as global tracer provider
trace.set_tracer_provider(tracer_provider)
```

## Configuration

Set your comprehend.dev ingestion token as an environment variable:

```bash
export COMPREHEND_OBSERVATIONS_TOKEN=your-ingestion-token-here
```

## What it captures

This integration automatically captures:

- **HTTP Routes** - API endpoints and their usage patterns
- **Database Operations** - SQL queries with table operations analysis
- **Service Dependencies** - HTTP client calls to external services
- **Performance Metrics** - Request durations, response codes, error rates
- **Service Architecture** - Automatically maps your service relationships

## Requirements

- Python 3.8+
- OpenTelemetry SDK
- An existing OpenTelemetry instrumentation setup

## Framework Support

Works with any Python framework that supports OpenTelemetry auto-instrumentation:

- FastAPI
- Django
- Flask
- SQLAlchemy
- Requests
- HTTPx
- And more...

## Learn More

- Visit [comprehend.dev](https://comprehend.dev) for documentation and to get your ingestion token
- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and release instructions.
