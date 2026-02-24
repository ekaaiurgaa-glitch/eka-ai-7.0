from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_tracing(app):
    """Setup distributed tracing with OTLP."""
    if not settings.JAEGER_ENDPOINT:
        logger.info("Tracing not configured")
        return
    
    try:
        trace.set_tracer_provider(TracerProvider())
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.JAEGER_ENDPOINT,
            insecure=True,
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        FastAPIInstrumentor.instrument_app(app)
        logger.info(f"Tracing enabled: {settings.JAEGER_ENDPOINT}")
    except Exception as e:
        logger.warning(f"Tracing setup failed: {e}")
