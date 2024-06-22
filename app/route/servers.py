from fastapi import APIRouter,       \
                    Depends

from route.login import get_current_user
from app.core.data_control.model.server_info import ServerInfo
from data_control import ServerInfoDataControl
from fastapi.responses import JSONResponse

servers_router = APIRouter(prefix='/api/servers')
OK_RESULT = {"message": "OK"}
OK_RESULT_RESPONSE_EXAMPLE = {200:{"content":
                               {"application/json":{"example":OK_RESULT}}
                             }}

@servers_router.get("/", response_model=set[ServerInfo])
async def get_servers_info():
    return ServerInfoDataControl().get_names()

@servers_router.post("/", response_model=None, dependencies=[Depends(get_current_user)],
                   responses=OK_RESULT_RESPONSE_EXAMPLE)
async def add_servers_info(info: ServerInfo):
    ServerInfoDataControl().add(info)
    return JSONResponse(OK_RESULT)

@servers_router.delete("/", response_model=None, dependencies=[Depends(get_current_user)], 
                     responses=OK_RESULT_RESPONSE_EXAMPLE)
async def delete_servers_info(info: ServerInfo):
    ServerInfoDataControl().remove(info)
    return JSONResponse(OK_RESULT)
