from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from api import router
from db import init_db
from logger import get_logger
import uvicorn

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown lifecycle."""
    try:
        logger.info("Starting CAIP application...")
        await init_db()
        yield
    except Exception as e:
        logger.exception(f"Startup error: {e}")
    finally:
        logger.info("CAIP application shutting down...")

app = FastAPI(title="Call Analytics & Insights Platform (CAIP)", lifespan=lifespan)
app.include_router(router, prefix="/api")



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title = "Call Analytics & Insights Platform",
        version="3.0.1",
        description="Checkout api(s) powered by CAIP engine",
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"]={
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

@app.get("/darkdocs", include_in_schema=False)
async def custom_swagger_ui_html_cdn():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_css_url="https://cdn.jsdelivr.net/gh/Itz-fork/Fastapi-Swagger-UI-Dark/assets/swagger_ui_dark.min.css"
    )


@app.get("/", include_in_schema=False)
async def index_path_to_server():
    return {"result": "Welcome to Call Analytics & Insights Platform Server"}

@app.get("/ping", include_in_schema=False)
async def ping_server():
    return {"result": "OK"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=42069)