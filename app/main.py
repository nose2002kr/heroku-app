from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from route.login import login_router
from route.video import video_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://nose2002kr.github.io/",
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
