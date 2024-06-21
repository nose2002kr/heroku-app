from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from route.login import login_router
from route.video import video_router
from route.servers import servers_router
from route.server import server_router

from service.service_message_consumer import ServiceMessageConsumer
from config import Config

import asyncio
import install_heroku # just import it

@asynccontextmanager
async def startup_event(app: FastAPI):
    asyncio.create_task(ServiceMessageConsumer().consume())
    yield


app = FastAPI(lifespan=startup_event)

origins = [
    "http://localhost:3000",
    "https://nose2002kr.github.io",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=login_router)
app.include_router(router=video_router)
app.include_router(router=server_router)
app.include_router(router=servers_router)
