from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from . import config
from .resources import shutdown, startup
from .routers import file, hello

routers = [
    file.router,
    hello.router,
]

app = FastAPI(
    title='Transfer',
    debug=config.DEBUG,
    default_response_class=ORJSONResponse,
    on_startup=(startup,),
    on_shutdown=(shutdown,),
)

for router in routers:
    app.include_router(router)
