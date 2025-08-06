"""Comprehensive tests for the observability module."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from campman_observability import (
    setup_tracing,
    setup_trace_context,
    get_trace_id,
    add_span_attributes,
    create_child_span,
)
from campman_observability.observability import (
    _parse_trace_context,
    _get_trace_context_from_sources,
    _update_log_fields_with_trace,
    _set_span_attribute,
    _get_current_trace_context,
)


class TestSetupTracing:
    """Test suite for setup_tracing function."""

    def test_setup_tracing_with_valid_params(self):
        """Test setup_tracing with valid parameters."""
        app = Flask(__name__)
        
        with patch('campman_observability.observability.FlaskInstrumentor') as mock_flask_instr, \
             patch('campman_observability.observability.RequestsInstrumentor') as mock_req_instr, \
             patch('campman_observability.observability.trace') as mock_trace, \
             patch('campman_observability.observability.set_global_textmap') as mock_set_textmap, \
             patch('campman_observability.observability.TracerProvider') as mock_tracer_provider, \
             patch('campman_observability.observability.CloudTraceSpanExporter') as mock_exporter:
            
            # Setup mocks
            mock_tracer = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            
            result = setup_tracing(app, "test-service", "test-namespace")
            
            # Verify instrumentors were called
            mock_flask_instr.return_value.instrument_app.assert_called_once_with(app)
            mock_req_instr.return_value.instrument.assert_called_once()
            
            # Verify result
            assert result == mock_tracer

    def test_setup_tracing_handles_exception_gracefully(self):
        """Test setup_tracing returns None when an exception occurs during setup."""
        app = Flask(__name__)
        
        with patch('campman_observability.observability.FlaskInstrumentor') as mock_flask_instr:
            # Make instrumentor raise an exception
            mock_flask_instr.side_effect = Exception("Test exception")
            
            result = setup_tracing(app, "test-service", "test-namespace")
            
            # Should return None and not raise
            assert result is None

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

    @patch('campman_observability.observability._get_trace_context_from_sources')
    @patch('campman_observability.observability._parse_trace_context')
    @patch('campman_observability.observability._update_log_fields_with_trace')
    @patch('campman_observability.observability._set_span_attribute')
    @patch('campman_observability.observability.get_current_span')
    def test_setup_trace_context_with_existing_trace(self, mock_get_span, mock_set_attr, 
                                                   mock_update_log, mock_parse, mock_get_sources):
        """Test setup_trace_context with existing trace context."""
        # Setup mocks
        mock_span = Mock()
        mock_get_span.return_value = mock_span
        mock_get_sources.return_value = ("test-trace-id/123;o=1", "HTTP headers")
        mock_parse.return_value = {
            'trace_id': 'test-trace-id',
            'span_id': '123',
            'sampled': True
        }
        
        global_log_fields = {}
        setup_trace_context("test-project", global_log_fields)
        
        # Verify calls
        mock_parse.assert_called_once_with("test-trace-id/123;o=1")
        mock_update_log.assert_called_once()
        mock_set_attr.assert_called_once()

    @patch('campman_observability.observability._get_trace_context_from_sources')
    @patch('campman_observability.observability._get_current_trace_context')
    @patch('campman_observability.observability._set_span_attribute')
    @patch('campman_observability.observability.get_current_span')
    def test_setup_trace_context_fallback_to_current(self, mock_get_span, mock_set_attr, 
                                                    mock_get_current, mock_get_sources):
        """Test setup_trace_context falls back to current context when no existing trace."""
        # Setup mocks
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_get_span.return_value = mock_span
        mock_get_sources.return_value = (None, None)
        mock_get_current.return_value = "current-trace/456;o=0"
        
        global_log_fields = {}
        setup_trace_context("test-project", global_log_fields)
        
        # Verify fallback was used
        mock_get_current.assert_called_once()
        mock_set_attr.assert_called_once_with(mock_span, "x-cloud-trace-context", "current-trace/456;o=0")


class TestParseTraceContext:
    """Test suite for _parse_trace_context function."""

    def test_parse_valid_trace_context_with_sampling(self):
        """Test parsing valid trace context with sampling flag."""
        result = _parse_trace_context("abcdef12345678901234567890123456/123456789;o=1")
        
        expected = {
            'trace_id': 'abcdef12345678901234567890123456',
            'span_id': '123456789',
            'sampled': True
        }
        assert result == expected

    def test_parse_valid_trace_context_without_sampling(self):
        """Test parsing valid trace context without sampling flag."""
        result = _parse_trace_context("abcdef12345678901234567890123456/123456789;o=0")
        
        expected = {
            'trace_id': 'abcdef12345678901234567890123456',
            'span_id': '123456789',
            'sampled': False
        }
        assert result == expected

    def test_parse_trace_context_without_options(self):
        """Test parsing trace context without options part."""
        result = _parse_trace_context("abcdef12345678901234567890123456/123456789")
        
        expected = {
            'trace_id': 'abcdef12345678901234567890123456',
            'span_id': '123456789',
            'sampled': False
        }
        assert result == expected

    def test_parse_invalid_trace_context_formats(self):
        """Test parsing various invalid trace context formats."""
        invalid_contexts = [
            "",
            None,
            "invalid",
            "trace-id-only",
            "trace-id/",
            "/span-id-only",
            "short-trace/123",  # trace_id too short
            "abc123def456789012345678901234567890/abc",  # non-numeric span_id
            "abc123def456789012345678901234567890/123;invalid",  # invalid options
            "abc123def456789012345678901234567890/123;o=2",  # invalid sampling flag
        ]
        
        for invalid_ctx in invalid_contexts:
            result = _parse_trace_context(invalid_ctx)
            assert result is None, f"Expected None for invalid context: {invalid_ctx}"

    def test_parse_trace_context_with_mixed_case_hex(self):
        """Test parsing trace context with mixed case hexadecimal trace_id."""
        result = _parse_trace_context("AbC123dEf45678901234567890123456/123456789;o=1")
        
        expected = {
            'trace_id': 'AbC123dEf45678901234567890123456',
            'span_id': '123456789',
            'sampled': True
        }
        assert result == expected


class TestGetTraceContextFromSources:
    """Test suite for _get_trace_context_from_sources function."""

    def test_get_from_pubsub_message(self):
        """Test getting trace context from Pub/Sub message attributes."""
        mock_request = Mock()
        mock_request.get_json.return_value = {
            "message": {
                "attributes": {
                    "x-cloud-trace-context": "pubsub-trace/789;o=1"
                }
            }
        }
        mock_request.headers.get.return_value = None
        
        with patch('campman_observability.observability.request', mock_request), \
             patch.dict(os.environ, {}, clear=True):
            result = _get_trace_context_from_sources()
        
        assert result == ("pubsub-trace/789;o=1", "Pub/Sub message attributes")

    def test_get_from_http_headers(self):
        """Test getting trace context from HTTP headers."""
        mock_request = Mock()
        mock_request.get_json.return_value = None
        mock_request.headers.get.return_value = "http-trace/456;o=0"
        
        with patch('campman_observability.observability.request', mock_request), \
             patch.dict(os.environ, {}, clear=True):
            result = _get_trace_context_from_sources()
        
        assert result == ("http-trace/456;o=0", "HTTP headers")

    def test_get_from_environment_variable(self):
        """Test getting trace context from environment variable."""
        mock_request = Mock()
        mock_request.get_json.return_value = None
        mock_request.headers.get.return_value = None
        
        with patch('campman_observability.observability.request', mock_request), \
             patch.dict(os.environ, {'TRACE_CONTEXT': 'env-trace/123;o=1'}):
            result = _get_trace_context_from_sources()
        
        assert result == ("env-trace/123;o=1", "environment variable")

    def test_get_no_trace_context_found(self):
        """Test when no trace context is found from any source."""
        mock_request = Mock()
        mock_request.get_json.return_value = None
        mock_request.headers.get.return_value = None
        
        with patch('campman_observability.observability.request', mock_request), \
             patch.dict(os.environ, {}, clear=True):
            result = _get_trace_context_from_sources()
        
        assert result == (None, None)

    def test_get_handles_malformed_pubsub_message(self):
        """Test handling malformed Pub/Sub message structure."""
        mock_request = Mock()
        mock_request.get_json.return_value = {"invalid": "structure"}
        mock_request.headers.get.return_value = None
        
        with patch('campman_observability.observability.request', mock_request), \
             patch.dict(os.environ, {}, clear=True):
            result = _get_trace_context_from_sources()
        
        assert result == (None, None)


class TestUpdateLogFieldsWithTrace:
    """Test suite for _update_log_fields_with_trace function."""

    def test_update_log_fields_success(self):
        """Test successful update of log fields with trace information."""
        global_log_fields = {}
        parsed_trace = {
            'trace_id': 'test-trace-id-12345678901234567890',
            'span_id': '987654321',
            'sampled': True
        }
        
        _update_log_fields_with_trace("test-project", global_log_fields, parsed_trace)
        
        expected_fields = {
            "logging.googleapis.com/trace": "projects/test-project/traces/test-trace-id-12345678901234567890",
            "logging.googleapis.com/spanId": "987654321",
            "logging.googleapis.com/trace_sampled": True
        }
        assert global_log_fields == expected_fields

    def test_update_log_fields_missing_trace_field(self):
        """Test handling missing required trace field."""
        global_log_fields = {}
        parsed_trace = {
            'trace_id': 'test-trace-id',
            # Missing span_id
            'sampled': True
        }
        
        with pytest.raises(KeyError):
            _update_log_fields_with_trace("test-project", global_log_fields, parsed_trace)


class TestSetSpanAttribute:
    """Test suite for _set_span_attribute function."""

    def test_set_span_attribute_success(self):
        """Test successfully setting span attribute."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        
        with patch('campman_observability.observability.context') as mock_context:
            _set_span_attribute(mock_span, "test-key", "test-value")
            
            mock_context.set_value.assert_called_once()
            mock_context.attach.assert_called_once()

    def test_set_span_attribute_no_recording_span(self):
        """Test setting attribute on non-recording span."""
        mock_span = Mock()
        mock_span.is_recording.return_value = False
        
        # Should not raise exception
        _set_span_attribute(mock_span, "test-key", "test-value")

    def test_set_span_attribute_none_span(self):
        """Test setting attribute on None span."""
        # Should not raise exception
        _set_span_attribute(None, "test-key", "test-value")


class TestGetCurrentTraceContext:
    """Test suite for _get_current_trace_context function."""

    @patch('campman_observability.observability.get_current_span')
    def test_get_current_trace_context_success(self, mock_get_span):
        """Test successfully getting current trace context."""
        mock_span = Mock()
        mock_span_context = Mock()
        mock_span_context.trace_id = 0xabc123def456789012345678901234567890
        mock_span_context.span_id = 123456789
        mock_span_context.trace_flags.sampled = True
        
        mock_span.get_span_context.return_value = mock_span_context
        mock_get_span.return_value = mock_span
        
        result = _get_current_trace_context()
        
        expected = "abc123def456789012345678901234567890/123456789;o=1"
        assert result == expected

    @patch('campman_observability.observability.get_current_span')
    def test_get_current_trace_context_exception(self, mock_get_span):
        """Test handling exception when getting current trace context."""
        mock_get_span.side_effect = Exception("Test error")
        
        result = _get_current_trace_context()
        
        # Should return fallback context
        assert result == "00000000000000000000000000000000/0;o=0"


class TestUtilityFunctions:
    """Test suite for utility functions."""

    @patch('campman_observability.observability.get_current_span')
    def test_get_trace_id_with_valid_span(self, mock_get_span):
        """Test get_trace_id returns trace ID from valid span."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_span_context = Mock()
        mock_span_context.trace_id = 0xabc123def456789012345678901234567890
        mock_span.get_span_context.return_value = mock_span_context
        mock_get_span.return_value = mock_span
        
        result = get_trace_id()
        
        assert result == "abc123def456789012345678901234567890"

    @patch('campman_observability.observability.get_current_span')
    def test_get_trace_id_with_no_span(self, mock_get_span):
        """Test get_trace_id returns None when no span is available."""
        mock_get_span.return_value = None
        result = get_trace_id()
        assert result is None

    @patch('campman_observability.observability.get_current_span')
    def test_get_trace_id_with_non_recording_span(self, mock_get_span):
        """Test get_trace_id returns None when span is not recording."""
        mock_span = Mock()
        mock_span.is_recording.return_value = False
        mock_get_span.return_value = mock_span
        
        result = get_trace_id()
        assert result is None

    @patch('campman_observability.observability.get_current_span')
    def test_add_span_attributes_success(self, mock_get_span):
        """Test successfully adding span attributes."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_get_span.return_value = mock_span
        
        add_span_attributes(test_attr="test_value", numeric_attr=123)
        
        # Verify attributes were set
        mock_span.set_attribute.assert_any_call("test_attr", "test_value")
        mock_span.set_attribute.assert_any_call("numeric_attr", "123")

    @patch('campman_observability.observability.get_current_span')
    def test_add_span_attributes_with_no_span(self, mock_get_span):
        """Test add_span_attributes handles missing span gracefully."""
        mock_get_span.return_value = None
        # Should not raise an exception
        add_span_attributes(test_attr="test_value")

    @patch('campman_observability.observability.get_current_span')
    def test_add_span_attributes_filters_none_values(self, mock_get_span):
        """Test add_span_attributes filters out None values."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_get_span.return_value = mock_span
        
        add_span_attributes(valid_attr="value", none_attr=None, empty_string_attr="")
        
        # Should call set_attribute twice: once for valid_attr and once for empty_string_attr
        # Empty string is a valid value, only None should be filtered out
        expected_calls = [
            (('valid_attr', 'value'),),
            (('empty_string_attr', ''),)
        ]
        assert mock_span.set_attribute.call_count == 2
        mock_span.set_attribute.assert_any_call("valid_attr", "value")
        mock_span.set_attribute.assert_any_call("empty_string_attr", "")

    @patch('campman_observability.observability.trace.get_tracer')
    def test_create_child_span_success(self, mock_get_tracer):
        """Test successfully creating a child span."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_get_tracer.return_value = mock_tracer
        
        result = create_child_span("test-span", test_attr="test_value")
        
        assert result == mock_span
        mock_tracer.start_span.assert_called_once_with("test-span")

    @patch('campman_observability.observability.trace.get_tracer')
    def test_create_child_span_returns_none_on_error(self, mock_get_tracer):
        """Test create_child_span returns None when creation fails."""
        mock_get_tracer.side_effect = Exception("Test error")
        result = create_child_span("test-span")
        assert result is None

    @patch('campman_observability.observability.trace.get_tracer')
    @patch('campman_observability.observability.add_span_attributes')
    def test_create_child_span_with_attributes(self, mock_add_attrs, mock_get_tracer):
        """Test creating child span with attributes."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_get_tracer.return_value = mock_tracer
        
        result = create_child_span("test-span", attr1="value1", attr2="value2")
        
        assert result == mock_span
        mock_add_attrs.assert_called_once_with(attr1="value1", attr2="value2")
