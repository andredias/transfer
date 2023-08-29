from fastapi import FastAPI

from . import config
from .resources import lifespan
from .routers import file, hello

app = FastAPI(
    title='Transfer',
    debug=config.DEBUG,
    lifespan=lifespan,
)
routers = (hello.router, file.router)
for router in routers:
    app.include_router(router)
