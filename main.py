from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging
import uvicorn
from api.api_v1.api import api_router
from core.config import settings
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def api_factory():
    app = FastAPI(
        title=settings.PROJECT_NAME
    )

    logging.config.dictConfig(settings.LOGGING_CONFIG)
    resource = Resource(attributes={"service.name": settings.PROJECT_NAME})
    '''tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)
    tracer.add_span_processor(BatchSpanProcessor(
        OTLPSpanExporter(endpoint=settings.TEMPO_URL)))
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)'''
    LoggingInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin)
                           for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = api_factory()


def run():
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = settings.LOGGING_CONFIG["formatters"]["standard"]["format"]
    uvicorn.run("main:app", log_config=log_config, reload=True)


if __name__ == "__main__":

    run()
