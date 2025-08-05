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

__version__ = "0.1.1"
__author__ = "Francesco Deleo"
__email__ = "francesco.deleo@ingka.com"

__all__ = [
    "setup_tracing",
    "setup_trace_context", 
    "get_trace_id",
    "add_span_attributes",
    "create_child_span",
]
