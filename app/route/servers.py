from fastapi import APIRouter,       \
                    Depends

from route.login import get_current_user
from servers_info import ServersInfo
from data_control import ServersInfoDataControl
from fastapi.responses import JSONResponse

servers_router = APIRouter(prefix='/api/servers')
OK_RESULT = {"message": "OK"}
OK_RESULT_RESPONSE_EXAMPLE = {200:{"content":
                               {"application/json":{"example":OK_RESULT}}
                             }}

@servers_router.get("/", response_model=set[ServersInfo])
async def get_servers_info():
    return ServersInfoDataControl.take_servers_infos()

@servers_router.post("/", response_model=None, dependencies=[Depends(get_current_user)],
                   responses=OK_RESULT_RESPONSE_EXAMPLE)
async def add_servers_info(info: ServersInfo):
    ServersInfoDataControl.add_servers_info(info)
    return JSONResponse(OK_RESULT)

@servers_router.delete("/", response_model=None, dependencies=[Depends(get_current_user)], 
                     responses=OK_RESULT_RESPONSE_EXAMPLE)
async def delete_servers_info(info: ServersInfo):
    ServersInfoDataControl.remove_servers_info(info)
    return JSONResponse(OK_RESULT)
