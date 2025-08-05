"""
Observability module for OpenTelemetry tracing setup and trace context management.

This module provides tracing capabilities for Flask applications with Google Cloud
Platform integration. It handles trace context propagation from HTTP requests, 
Pub/Sub messages or environment variables using GCP's Cloud Trace format 
("x-cloud-trace-context": "TRACE_ID/SPAN_ID;o=SAMPLED_FLAG").

Key Features:
- Flask and requests instrumentation
- GCP Cloud Trace integration
- Trace context parsing and propagation
- Robust error handling with fallbacks
- Utility functions for span management

Usage:
    from libs.Observability import setup_tracing, setup_trace_context
    
    # Setup tracing for Flask app
    app = Flask(__name__)
    tracer = setup_tracing(app)
    
    # Setup trace context in request handlers
    @app.route("/", methods=["GET"])
    def main():
        setup_trace_context(project_id, global_log_fields)
        # Your code here

    @app.route("/trigger-via-pubsub", methods=["POST"])
    def trigger_via_pubsub():
        setup_trace_context(project_id, global_log_fields)
        # Your code here
"""

import json
import logging
import os
from typing import Dict, Optional, Tuple, Union

from flask import Flask, request
from opentelemetry import trace, context
from opentelemetry.trace import get_current_span, Tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import CloudTraceFormatPropagator

# Configure logger
logger = logging.getLogger(__name__)

# Constants
TRACE_HEADER_KEY = "x-cloud-trace-context"
HTTP_TRACE_HEADER = "X-Cloud-Trace-Context"

def setup_tracing(
    app: Flask, 
    service_name: str, 
    service_namespace: str
) -> Optional[Tracer]:
    """
    Set up OpenTelemetry tracing for Flask app and requests.
    
    Args:
        app: Flask application instance
        service_name: Name of the service for tracing (required)
        service_namespace: Namespace for the service (required)
    
    Returns:
        tracer: Configured tracer instance, or None if setup fails
    
    Raises:
        ValueError: If required parameters are missing or invalid
    
    Note:
        This function will raise exceptions for configuration errors (missing required params)
        but will not raise exceptions for runtime tracing setup failures to avoid breaking 
        the main application flow.
    """
    if not app:
        raise ValueError("Flask app instance is required for tracing setup")

    if not service_name or not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("service_name is required and must be a non-empty string")
        
    if not service_namespace or not isinstance(service_namespace, str) or not service_namespace.strip():
        raise ValueError("service_namespace is required and must be a non-empty string")
    
    try:
        # Instrument Flask and requests
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()
        
        # Create resource with service information
        resource = Resource.create({
            "service.name": service_name,
            "service.namespace": service_namespace,
            "service.instance.id": f"worker-{os.getpid()}",
        })
        
        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(CloudTraceSpanExporter())
        )
        
        # Set up propagator
        set_global_textmap(CloudTraceFormatPropagator())
        
        logger.info(f"Tracing setup completed for service: {service_name}")
        return trace.get_tracer(__name__)
        
    except Exception as e:
        logger.error(f"Failed to setup tracing: {e}. Application will continue without tracing.")
        # Return None instead of raising to allow application to continue
        return None
     
def setup_trace_context(project_id: str, global_log_fields: Dict[str, Union[str, bool]]) -> None:
    """
    Unified function to handle trace context.
    Updates global_log_fields with trace information and sets span attributes.
    
    Args:
        project_id: GCP project ID for trace formatting
        global_log_fields: Dictionary to update with trace fields
        
    Raises:
        ValueError: If project_id is not provided
    """
    if not project_id:
        raise ValueError("project_id is required")
    
    if not isinstance(global_log_fields, dict):
        raise ValueError("global_log_fields must be a dictionary")
    
    try:
        current_span = get_current_span()
        
        # Try to get trace header from Pub/Sub message or HTTP headers or environment variable
        trace_ctx_str, source = _get_trace_context_from_sources()
        
        if trace_ctx_str:
            parsed_trace = _parse_trace_context(trace_ctx_str)
            if parsed_trace:
                _update_log_fields_with_trace(project_id, global_log_fields, parsed_trace)
                _set_span_attribute(current_span, TRACE_HEADER_KEY, trace_ctx_str)
                logger.debug(f"Using existing trace_id: {parsed_trace['trace_id']} from {source}")
                return
        
        # Fall back to current context
        if current_span.is_recording():
            trace_ctx_str = _get_current_trace_context()
            _set_span_attribute(current_span, TRACE_HEADER_KEY, trace_ctx_str)
            logger.debug("No existing trace found. Using current context.")
            
    except Exception as e:
        logger.error(f"Error setting up trace context: {e}")
        # Don't re-raise to avoid breaking the main flow

def _get_trace_context_from_sources() -> Tuple[Optional[str], Optional[str]]:
    """
    Get trace header from Pub/Sub message, HTTP headers, or environment variable.
    
    Returns:
        Tuple of (trace_context_string, source) or (None, None) if not found
    """
    # Try Pub/Sub first
    try:
        envelope = request.get_json(silent=True)
        if envelope and isinstance(envelope, dict):
            pubsub_message = envelope.get("message", {})
            if isinstance(pubsub_message, dict):
                attributes = pubsub_message.get("attributes", {})
                if isinstance(attributes, dict):
                    trace_ctx_str = attributes.get(TRACE_HEADER_KEY)
                    if trace_ctx_str:
                        return trace_ctx_str, "Pub/Sub message attributes"
    except Exception as e:
        logger.debug(f"Failed to get trace context from Pub/Sub: {e}")
    
    # Try HTTP headers
    try:
        trace_ctx_str = request.headers.get(HTTP_TRACE_HEADER)
        if trace_ctx_str:
            return trace_ctx_str, "HTTP headers"
    except Exception as e:
        logger.debug(f"Failed to get trace context from HTTP headers: {e}")

    # Try environment variable as fallback
    try:
        trace_ctx_str = os.environ.get('TRACE_CONTEXT')
        if trace_ctx_str:
            return trace_ctx_str, "environment variable"
    except Exception as e:
        logger.debug(f"Failed to get trace context from environment variable: {e}")
        
    return None, None


def _update_log_fields_with_trace(
    project_id: str, 
    global_log_fields: Dict[str, Union[str, bool]], 
    parsed_trace: Dict[str, Union[str, bool]]
) -> None:
    """
    Update global log fields with trace information.
    
    Args:
        project_id: GCP project ID
        global_log_fields: Dictionary to update with trace fields
        parsed_trace: Parsed trace information
    """
    try:
        global_log_fields["logging.googleapis.com/trace"] = f"projects/{project_id}/traces/{parsed_trace['trace_id']}"
        global_log_fields["logging.googleapis.com/spanId"] = parsed_trace['span_id']
        global_log_fields["logging.googleapis.com/trace_sampled"] = parsed_trace['sampled']
    except KeyError as e:
        logger.error(f"Missing required trace field: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to update log fields with trace: {e}")
        raise


def _set_span_attribute(current_span, key: str, value: str) -> None:
    """
    Set attribute in span context safely.
    
    Args:
        current_span: Current OpenTelemetry span
        key: Attribute key
        value: Attribute value
    """
    try:
        if current_span and current_span.is_recording():
            updated_context = context.set_value("CONTEXT_ATTRIBUTES_KEY", {key: value})
            context.attach(updated_context)
    except Exception as e:
        logger.debug(f"Failed to set span attribute: {e}")
        # Don't raise to avoid breaking the main flow
    
def _parse_trace_context(trace_ctx_str: str) -> Optional[Dict[str, Union[str, bool]]]:
    """
    Parse GCP x-cloud-trace-context header format: TRACE_ID/SPAN_ID;o=SAMPLED_FLAG
    
    Args:
        trace_ctx_str: The x-cloud-trace-context header value
        
    Returns:
        Dictionary containing trace_id, span_id, and sampled flag
        Returns None if parsing fails
    """
    if not trace_ctx_str or not isinstance(trace_ctx_str, str):
        return None
    
    try:
        # Split by semicolon to separate trace/span from options
        parts = trace_ctx_str.split(';')
        if not parts:
            return None
            
        trace_span_part = parts[0].strip()
        if not trace_span_part:
            return None
        
        # Extract trace_id and span_id
        trace_span_components = trace_span_part.split('/')
        if len(trace_span_components) != 2:
            logger.debug(f"Invalid trace context format: {trace_ctx_str}")
            return None
            
        trace_id = trace_span_components[0].strip()
        span_id = trace_span_components[1].strip()
        
        # Validate trace_id and span_id are not empty
        if not trace_id or not span_id:
            logger.debug(f"Empty trace_id or span_id in: {trace_ctx_str}")
            return None
        
        # Validate trace_id format (should be 32 hex characters)
        if len(trace_id) != 32 or not all(c in '0123456789abcdefABCDEF' for c in trace_id):
            logger.debug(f"Invalid trace_id format: {trace_id}")
            return None
            
        # Validate span_id format (should be numeric)
        try:
            int(span_id)
        except ValueError:
            logger.debug(f"Invalid span_id format: {span_id}")
            return None
        
        # Extract sampled flag (default to False)
        sampled = False
        if len(parts) > 1:
            options_part = parts[1].strip()
            # Check for o=1 (sampled) or o=0 (not sampled)
            if options_part.startswith('o='):
                if options_part in ('o=0', 'o=1'):
                    sampled = options_part == 'o=1'
                else:
                    logger.debug(f"Invalid sampled flag: {options_part}")
                    return None
            else:
                logger.debug(f"Invalid options format: {options_part}")
                return None
        
        return {
            'trace_id': trace_id,
            'span_id': span_id,
            'sampled': sampled
        }
        
    except (IndexError, ValueError, AttributeError) as e:
        logger.debug(f"Failed to parse trace context '{trace_ctx_str}': {e}")
        return None


def _get_current_trace_context() -> str:
    """
    Get current trace context in Cloud Trace format.
    
    Returns:
        Trace context string in format: TRACE_ID/SPAN_ID;o=SAMPLED_FLAG
    """
    try:
        span = get_current_span()
        span_context = span.get_span_context()

        trace_id = format(span_context.trace_id, "032x")
        span_id = str(span_context.span_id)
        sampled_flag = "1" if span_context.trace_flags.sampled else "0"

        return f"{trace_id}/{span_id};o={sampled_flag}"
        
    except Exception as e:
        logger.error(f"Failed to get current trace context: {e}")
        # Return a minimal valid context
        return "00000000000000000000000000000000/0;o=0"


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID for logging purposes.
    
    Returns:
        The current trace ID as a string, or None if not available
    """
    try:
        span = get_current_span()
        if span and span.is_recording():
            span_context = span.get_span_context()
            return format(span_context.trace_id, "032x")
    except Exception as e:
        logger.debug(f"Failed to get trace ID: {e}")
    return None


def add_span_attributes(**attributes) -> None:
    """
    Add custom attributes to the current span.
    
    Args:
        **attributes: Key-value pairs to add as span attributes
    """
    try:
        span = get_current_span()
        if span and span.is_recording():
            for key, value in attributes.items():
                if key and value is not None:
                    span.set_attribute(str(key), str(value))
    except Exception as e:
        logger.debug(f"Failed to add span attributes: {e}")


def create_child_span(name: str, **attributes) -> Optional[trace.Span]:
    """
    Create a child span with the given name and attributes.
    
    Args:
        name: Name of the span
        **attributes: Additional attributes to set on the span
        
    Returns:
        The created span or None if creation fails
    """
    try:
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span(name)
        if attributes:
            add_span_attributes(**attributes)
        return span
    except Exception as e:
        logger.error(f"Failed to create child span '{name}': {e}")
        return None