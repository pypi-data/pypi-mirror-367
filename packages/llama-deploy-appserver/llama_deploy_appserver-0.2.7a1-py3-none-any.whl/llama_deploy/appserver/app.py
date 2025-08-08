import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse

from .routers import deployments_router, status_router
from .server import lifespan, manager
from .settings import settings
from .tracing import configure_tracing


logger = logging.getLogger("uvicorn.info")


app = FastAPI(lifespan=lifespan)

# Setup tracing
configure_tracing(settings)

# Configure CORS middleware if the environment variable is set
if not os.environ.get("DISABLE_CORS", False):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(deployments_router)
app.include_router(status_router)


@app.get("/", response_model=None)
async def root(request: Request) -> JSONResponse | RedirectResponse:
    # for local dev, just redirect to the one UI if we have one
    if len(manager.deployment_names) == 1:
        deployment = manager.get_deployment(manager.deployment_names[0])
        if deployment is not None and deployment._ui_server_process is not None:
            return RedirectResponse(f"deployments/{deployment.name}/ui")
    return JSONResponse(
        {
            "swagger_docs": f"{request.base_url}docs",
            "status": f"{request.base_url}status",
        }
    )
