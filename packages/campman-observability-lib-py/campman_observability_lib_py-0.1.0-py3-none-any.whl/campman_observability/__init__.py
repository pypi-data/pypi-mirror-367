"""
Campman Observability Library

A Python library for OpenTelemetry observability setup with Google Cloud Platform integration.
"""

from .observability import (
    setup_tracing,
    setup_trace_context,
    get_trace_id,
    add_span_attributes,
    create_child_span,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "setup_tracing",
    "setup_trace_context", 
    "get_trace_id",
    "add_span_attributes",
    "create_child_span",
]
