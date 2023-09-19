from fastapi import FastAPI

from . import config
from .resources import lifespan
from .routers import file

app = FastAPI(
    title='Transfer',
    debug=config.DEBUG,
    lifespan=lifespan,
)
routers = (file.router,)
for router in routers:
    app.include_router(router)
