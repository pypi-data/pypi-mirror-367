"""Basic tests for the observability module."""

import pytest
from unittest.mock import Mock, patch
from flask import Flask

from campman_observability import (
    setup_tracing,
    setup_trace_context,
    get_trace_id,
    add_span_attributes,
    create_child_span,
)


class TestSetupTracing:
    """Test suite for setup_tracing function."""

    def test_setup_tracing_with_valid_params(self):
        """Test setup_tracing with valid parameters."""
        app = Flask(__name__)
        
        with patch('campman_observability.observability.FlaskInstrumentor') as mock_flask_instr, \
             patch('campman_observability.observability.RequestsInstrumentor') as mock_req_instr, \
             patch('campman_observability.observability.trace') as mock_trace:
            
            result = setup_tracing(app, "test-service", "test-namespace")
            
            # Verify instrumentors were called
            mock_flask_instr.return_value.instrument_app.assert_called_once_with(app)
            mock_req_instr.return_value.instrument.assert_called_once()

    def test_setup_tracing_missing_app(self):
        """Test setup_tracing raises ValueError when app is missing."""
        with pytest.raises(ValueError, match="Flask app instance is required"):
            setup_tracing(None, "test-service", "test-namespace")

    def test_setup_tracing_missing_service_name(self):
        """Test setup_tracing raises ValueError when service_name is missing."""
        app = Flask(__name__)
        with pytest.raises(ValueError, match="service_name is required"):
            setup_tracing(app, "", "test-namespace")

    def test_setup_tracing_missing_service_namespace(self):
        """Test setup_tracing raises ValueError when service_namespace is missing."""
        app = Flask(__name__)
        with pytest.raises(ValueError, match="service_namespace is required"):
            setup_tracing(app, "test-service", "")


class TestSetupTraceContext:
    """Test suite for setup_trace_context function."""

    def test_setup_trace_context_missing_project_id(self):
        """Test setup_trace_context raises ValueError when project_id is missing."""
        with pytest.raises(ValueError, match="project_id is required"):
            setup_trace_context("", {})

    def test_setup_trace_context_invalid_global_log_fields(self):
        """Test setup_trace_context raises ValueError when global_log_fields is not a dict."""
        with pytest.raises(ValueError, match="global_log_fields must be a dictionary"):
            setup_trace_context("test-project", "not-a-dict")


class TestUtilityFunctions:
    """Test suite for utility functions."""

    def test_get_trace_id_with_no_span(self):
        """Test get_trace_id returns None when no span is available."""
        with patch('campman_observability.observability.get_current_span') as mock_get_span:
            mock_get_span.return_value = None
            result = get_trace_id()
            assert result is None

    def test_add_span_attributes_with_no_span(self):
        """Test add_span_attributes handles missing span gracefully."""
        with patch('campman_observability.observability.get_current_span') as mock_get_span:
            mock_get_span.return_value = None
            # Should not raise an exception
            add_span_attributes(test_attr="test_value")

    def test_create_child_span_returns_none_on_error(self):
        """Test create_child_span returns None when creation fails."""
        with patch('campman_observability.observability.trace.get_tracer') as mock_get_tracer:
            mock_get_tracer.side_effect = Exception("Test error")
            result = create_child_span("test-span")
            assert result is None
