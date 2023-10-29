from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from . import config  # noqa: F401
from .exception_handlers import request_validation_exception_handler
from .middleware import log_request_middleware
from .resources import lifespan
from .routers import file

app = FastAPI(
    title='Transfer',
    lifespan=lifespan,
)

routers = (file.router,)
for router in routers:
    app.include_router(router)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
