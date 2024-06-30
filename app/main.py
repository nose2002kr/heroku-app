from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from route.login import login_router
from route.video import video_router
from route.servers import servers_router
from route.server import server_router
from route.github_rank import github_rank_router

from app.service.server_message_consumer import ServerMessageConsumer

import asyncio
from app.config import Config

@asynccontextmanager
async def startup_event(app: FastAPI):
    asyncio.create_task(ServerMessageConsumer().consume())
    redis = aioredis.from_url('redis://default:' + Config.redis_pwd + '@' + Config.redis_host + ':' + Config.redis_port)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
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
app.include_router(router=github_rank_router)

