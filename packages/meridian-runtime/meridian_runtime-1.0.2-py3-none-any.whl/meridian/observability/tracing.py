from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any
import uuid

# Context variables for tracing
_current_trace_id: ContextVar[str | None] = ContextVar("current_trace_id", default=None)
_current_span_id: ContextVar[str | None] = ContextVar("current_span_id", default=None)


@dataclass
class TracingConfig:
    """
    Configuration for tracing behavior and provider selection.

    Attributes:
      enabled:
        When True, tracing spans are recorded via the configured provider.
      provider:
        Tracing backend identifier. Supported values:
          - "noop": disable spans (no-op tracer)
          - "inmemory": in-memory tracer for development/testing
          - "opentelemetry": OpenTelemetry integration for production use
      sample_rate:
        Fraction (0.0–1.0) indicating the portion of operations sampled.
        Used by OpenTelemetry tracer; other providers may ignore this setting.
    """

    enabled: bool = False
    provider: str = "noop"  # "opentelemetry" | "inmemory" | "noop"
    sample_rate: float = 0.0


class Span:
    """Represents a tracing span with a name, trace_id, and span_id."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.attributes = attributes or {}
        self._finished = False

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        if not self._finished:
            self.attributes[key] = value

    def finish(self) -> None:
        """Mark the span as finished."""
        self._finished = True

    def is_finished(self) -> bool:
        """Check if the span is finished."""
        return self._finished


class NoopSpan(Span):
    """No-op span implementation that ignores all operations."""

    def __init__(self, name: str) -> None:
        super().__init__(name, "", "")

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def finish(self) -> None:
        pass


class Tracer:
    """
    Base tracer interface.

    Responsibilities:
      - Create spans that capture timing and attributes for traced operations.
      - Report whether tracing is enabled (e.g., for conditional instrumentation).
    """

    def __init__(self, config: TracingConfig) -> None:
        self._config = config

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        """
        Start a new span.
        
        Parameters:
          name: Name of the operation being traced.
          attributes: Optional key-value attributes to attach to the span.
          
        Returns:
          A Span instance for the traced operation.
        """
        raise NotImplementedError

    def is_enabled(self) -> bool:
        """Return True if tracing is enabled per the tracer's configuration."""
        return self._config.enabled


class NoopTracer(Tracer):
    """No-op tracer implementation that returns NoopSpan instances."""

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        return NoopSpan(name)


class InMemoryTracer(Tracer):
    """
    In-memory tracer for testing and development.

    Semantics:
      - Stores created spans in memory for later inspection via get_spans().
      - Respects the enabled flag; returns NoopSpan when disabled.
      - Generates UUID-based trace_id and span_id values by default.
    """

    def __init__(self, config: TracingConfig) -> None:
        super().__init__(config)
        self.spans: list[Span] = []

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        if not self._config.enabled:
            return NoopSpan(name)

        # Get or generate trace ID
        trace_id = _current_trace_id.get() or self._generate_trace_id()
        span_id = self._generate_span_id()

        span = Span(name, trace_id, span_id, attributes)
        self.spans.append(span)
        return span

    def _generate_trace_id(self) -> str:
        """Generate a new trace ID."""
        return str(uuid.uuid4())

    def _generate_span_id(self) -> str:
        """Generate a new span ID."""
        return str(uuid.uuid4())

    def get_spans(self) -> list[Span]:
        """Get all recorded spans."""
        return self.spans.copy()

    def clear_spans(self) -> None:
        """Clear all recorded spans."""
        self.spans.clear()


class OpenTelemetryTracer(Tracer):
    """
    OpenTelemetry tracer implementation.

    Semantics:
      - Integrates with OpenTelemetry SDK when available.
      - Falls back to NoopSpan when OpenTelemetry is not installed or disabled.
      - Respects sampling configuration from TracingConfig.
    """

    def __init__(self, config: TracingConfig) -> None:
        super().__init__(config)
        self._otel_tracer = None
        self._initialize_otel()

    def _initialize_otel(self) -> None:
        """Initialize OpenTelemetry tracer if available."""
        if not self._config.enabled:
            return

        try:
            # Try to import OpenTelemetry
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.sampling import TraceIdRatioBasedSampler
            
            # Configure sampling based on config
            sampler = TraceIdRatioBasedSampler(self._config.sample_rate)
            
            # Set up tracer provider if not already configured
            if not isinstance(trace.get_tracer_provider(), TracerProvider):
                trace.set_tracer_provider(TracerProvider(sampler=sampler))
            
            # Get tracer instance
            self._otel_tracer = trace.get_tracer("meridian-runtime")
            
        except ImportError:
            # OpenTelemetry not available, will fall back to NoopSpan
            pass
        except Exception:
            # Any other error in OpenTelemetry setup, fall back gracefully
            pass

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        if not self._config.enabled or self._otel_tracer is None:
            return NoopSpan(name)

        try:
            # Start OpenTelemetry span
            otel_span = self._otel_tracer.start_span(name)
            
            # Set attributes if provided
            if attributes:
                for key, value in attributes.items():
                    otel_span.set_attribute(key, str(value))
            
            # Extract trace and span IDs
            span_context = otel_span.get_span_context()
            trace_id = format(span_context.trace_id, '032x')
            span_id = format(span_context.span_id, '016x')
            
            # Create our span wrapper
            span = OpenTelemetrySpan(name, trace_id, span_id, otel_span, attributes)
            return span
            
        except Exception:
            # Fall back to NoopSpan on any error
            return NoopSpan(name)


class OpenTelemetrySpan(Span):
    """Span implementation that wraps an OpenTelemetry span."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        otel_span: Any,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, trace_id, span_id, attributes)
        self._otel_span = otel_span

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on both our span and the OpenTelemetry span."""
        if not self._finished:
            self.attributes[key] = value
            try:
                self._otel_span.set_attribute(key, str(value))
            except Exception:
                # Ignore errors in OpenTelemetry attribute setting
                pass

    def finish(self) -> None:
        """Mark the span as finished and end the OpenTelemetry span."""
        if not self._finished:
            self._finished = True
            try:
                self._otel_span.end()
            except Exception:
                # Ignore errors in OpenTelemetry span ending
                pass


# Global tracer instance
_global_tracer: Tracer = NoopTracer(TracingConfig())


def get_tracer() -> Tracer:
    """Get the global tracer instance (NoopTracer by default)."""
    return _global_tracer


def configure_tracing(config: TracingConfig) -> None:
    """
    Configure the global tracer.

    Parameters:
      config:
        TracingConfig specifying provider and enablement.

    Provider mapping:
      - "inmemory": use InMemoryTracer (development/testing)
      - "opentelemetry": use OpenTelemetryTracer (production)
      - any other value: use NoopTracer (disabled)

    Notes:
      - OpenTelemetry tracer requires the opentelemetry-sdk package to be installed.
      - If OpenTelemetry is not available, falls back to NoopTracer gracefully.
    """
    global _global_tracer

    if config.provider == "inmemory":
        _global_tracer = InMemoryTracer(config)
    elif config.provider == "opentelemetry":
        _global_tracer = OpenTelemetryTracer(config)
    else:
        _global_tracer = NoopTracer(config)


@contextmanager
def start_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[Span]:
    """
    Context manager that creates and manages a span.

    Parameters:
      name:
        Operation or scope name for the span.
      attributes:
        Optional key/value attributes to annotate the span.

    Behavior:
      - Starts a span via the global tracer and sets current trace/span IDs.
      - Yields the span to the caller's context.
      - Finishes the span and restores prior context on exit.
      - If tracing is disabled, returns a NoopSpan and still preserves API flow.

    Returns:
      Iterator yielding the started Span (or NoopSpan).
    """
    tracer = get_tracer()
    span = tracer.start_span(name, attributes)

    # Set span context
    old_trace_id = _current_trace_id.get()
    old_span_id = _current_span_id.get()

    trace_token = _current_trace_id.set(span.trace_id) if span.trace_id else None
    span_token = _current_span_id.set(span.span_id) if span.span_id else None

    try:
        yield span
    finally:
        span.finish()

        # Restore context
        if trace_token:
            _current_trace_id.set(old_trace_id)
        if span_token:
            _current_span_id.set(old_span_id)


def set_trace_id(trace_id: str) -> None:
    """Set the trace ID for the current tracing context."""
    _current_trace_id.set(trace_id)


def get_trace_id() -> str | None:
    """Get the current trace ID from the tracing context."""
    return _current_trace_id.get()


def get_span_id() -> str | None:
    """Get the current span ID from the tracing context."""
    return _current_span_id.get()


def generate_trace_id() -> str:
    """Generate a new random trace ID (UUID string)."""
    return str(uuid.uuid4())


def is_tracing_enabled() -> bool:
    """Return True if tracing is currently enabled on the global tracer."""
    return get_tracer().is_enabled()
