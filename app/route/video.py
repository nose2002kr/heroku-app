from fastapi import APIRouter,       \
                    Depends

from route.login import get_current_user
from video_info import VideoInfo
from data_control import VideoInfoDataControl
from fastapi.responses import JSONResponse

video_router = APIRouter(prefix='/api/video')
OK_RESULT = {"message": "OK"}
OK_RESULT_RESPONSE_EXAMPLE = {200:{"content":
                               {"application/json":{"example":OK_RESULT}}
                             }}

@video_router.get("/", response_model=set[VideoInfo])
async def get_video_infos():
    return VideoInfoDataControl.take_video_infos()

@video_router.post("/", response_model=None, dependencies=[Depends(get_current_user)],
                   responses=OK_RESULT_RESPONSE_EXAMPLE)
async def add_video_info(info: VideoInfo):
    VideoInfoDataControl.add_video_info(info)

@video_router.delete("/", response_model=None, dependencies=[Depends(get_current_user)], 
                     responses=OK_RESULT_RESPONSE_EXAMPLE)
async def delete_video_info(info: VideoInfo):
    VideoInfoDataControl.remove_video_info(info)
    return JSONResponse(OK_RESULT)
