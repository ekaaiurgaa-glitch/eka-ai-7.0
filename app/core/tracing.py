from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_tracing(app):
    """Setup distributed tracing with Jaeger."""
    if not settings.JAEGER_ENDPOINT:
        logger.info("Jaeger not configured, tracing disabled")
        return
    
    try:
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=settings.JAEGER_HOST,
            agent_port=settings.JAEGER_PORT,
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        FastAPIInstrumentor.instrument_app(app)
        logger.info(f"Tracing enabled: {settings.JAEGER_HOST}:{settings.JAEGER_PORT}")
    except Exception as e:
        logger.warning(f"Tracing setup failed: {e}")
