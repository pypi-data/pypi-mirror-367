# Campman Observability Library

A Python library for OpenTelemetry observability setup with Google Cloud Platform integration, specifically designed for Flask applications.

## Features

- **Flask and Requests Instrumentation**: Automatic tracing for Flask applications and HTTP requests
- **GCP Cloud Trace Integration**: Seamless integration with Google Cloud Trace
- **Trace Context Propagation**: Handles trace context from HTTP requests, Pub/Sub messages, and environment variables
- **Robust Error Handling**: Graceful fallbacks to ensure your application continues running even if tracing fails
- **Utility Functions**: Convenient functions for span management and trace context handling

## Installation

```bash
pip install campman-observability-lib-py
```

## Quick Start

```python
from flask import Flask
from campman_observability import setup_tracing, setup_trace_context

app = Flask(__name__)

# Setup tracing for your Flask app
tracer = setup_tracing(
    app=app,
    service_name="my-service",
    service_namespace="my-namespace"
)

@app.route("/")
def main():
    # Setup trace context in request handlers
    setup_trace_context(
        project_id="your-gcp-project-id",
        global_log_fields={}
    )
    return "Hello, World!"

@app.route("/trigger-via-pubsub", methods=["POST"])
def trigger_via_pubsub():
    setup_trace_context(
        project_id="your-gcp-project-id",
        global_log_fields={}
    )
    return "Handled Pub/Sub trigger"

if __name__ == "__main__":
    app.run()
```

## API Reference

### `setup_tracing(app, service_name, service_namespace)`

Set up OpenTelemetry tracing for a Flask application.

**Parameters:**
- `app` (Flask): Flask application instance
- `service_name` (str): Name of the service for tracing
- `service_namespace` (str): Namespace for the service

**Returns:**
- `Tracer`: Configured tracer instance, or `None` if setup fails

**Raises:**
- `ValueError`: If required parameters are missing or invalid

### `setup_trace_context(project_id, global_log_fields)`

Set up trace context from various sources (HTTP headers, Pub/Sub messages, environment variables).

**Parameters:**
- `project_id` (str): GCP project ID for trace formatting
- `global_log_fields` (dict): Dictionary to update with trace fields

**Raises:**
- `ValueError`: If `project_id` is not provided or `global_log_fields` is not a dictionary

### `get_trace_id()`

Get the current trace ID for logging purposes.

**Returns:**
- `str`: The current trace ID, or `None` if not available

### `add_span_attributes(**attributes)`

Add custom attributes to the current span.

**Parameters:**
- `**attributes`: Key-value pairs to add as span attributes

### `create_child_span(name, **attributes)`

Create a child span with the given name and attributes.

**Parameters:**
- `name` (str): Name of the span
- `**attributes`: Additional attributes to set on the span

**Returns:**
- `Span`: The created span or `None` if creation fails

## Trace Context Sources

The library automatically detects and uses trace context from multiple sources:

1. **Pub/Sub Messages**: Extracts trace context from message attributes
2. **HTTP Headers**: Reads `X-Cloud-Trace-Context` header
3. **Environment Variables**: Falls back to `TRACE_CONTEXT` environment variable
4. **Current Context**: Uses the current OpenTelemetry context as final fallback

## GCP Cloud Trace Format

The library uses Google Cloud Trace format for trace context:
```
TRACE_ID/SPAN_ID;o=SAMPLED_FLAG
```

Where:
- `TRACE_ID`: 32-character hexadecimal string
- `SPAN_ID`: Numeric span identifier
- `SAMPLED_FLAG`: `1` for sampled, `0` for not sampled

## Error Handling

The library is designed with robust error handling:
- Configuration errors (missing required parameters) raise `ValueError`
- Runtime tracing failures are logged but don't break application flow
- Graceful fallbacks ensure your application continues running

## Development

### Setting up development environment

```bash
git clone https://github.com/yourusername/campman-observability-lib-py.git
cd campman-observability-lib-py
pip install -e .[dev]
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black .
flake8 .
mypy .
```

## Requirements

- Python 3.8+
- Flask 3.1.1+
- OpenTelemetry packages (see requirements.txt)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/yourusername/campman-observability-lib-py/issues).
