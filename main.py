from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging
import uvicorn
from api.api_v1.api import api_router
from core.config import settings
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi


def api_factory():
    app = FastAPI(title=settings.PROJECT_NAME,
                  root_path="/Template",
                  version='0.0.1',
                  description='Template para criação de APIs',
                  )
    logging.config.dictConfig(settings.LOGGING_CONFIG)
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


@app.get(f"{app.root_path}/", description='Resposta somente para validar se a API subiu corretamente. Sem nenhuma conexão com o banco de dados.',
         summary='Valida se API está no ar')
def get_index():
    return {'msg': 'API está no ar!'}


@app.get(f"{app.root_path}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/Template/openapi.json", title='API Docs')

# Rota para a documentação Redoc


@app.get(f"{app.root_path}/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(openapi_url="/Template/openapi.json", title='ReDoc')

'''Rota para o esquema OpenAPI'''


@app.get(f"{app.root_path}/openapi.json", include_in_schema=False)
async def get_custom_openapi():
    return get_openapi(title=app.title, version="0.0.1", routes=app.routes, description=app.description)


def run():
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = settings.LOGGING_CONFIG["formatters"]["standard"]["format"]
    uvicorn.run("main:app", log_config=log_config, reload=True)


if __name__ == "__main__":

    run()
