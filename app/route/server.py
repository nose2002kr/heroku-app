from fastapi import APIRouter,       \
                    WebSocket,       \
                    WebSocketDisconnect,\
                    HTTPException,   \
                    Depends
from route.login import get_current_user
from types import SimpleNamespace
from app.core.data_control import ServerCommandInfoDataControl, ServerPowerStatusInfoDataControl
from app.core.data_control.model.server_command_info import Protocol
from service.server_cli import request_to_proceed_commend_on_cli
from app.service.server_message_producer import ServerMessageProducer

from config import Config
from loguru import logger

server_router = APIRouter(prefix='/api/server')
OK_RESULT = {"message": "OK"}
OK_RESULT_RESPONSE_EXAMPLE = {200:{"content":
                               {"application/json":{"example":OK_RESULT}}
                             }}
@server_router.websocket("/{server_name}/run")
async def run_to_server(websocket: WebSocket, server_name: str):
    token = websocket.query_params.get('token')
    await websocket.accept()
    try:
        logger.debug(f'accepted, token: {token}')
        payload = await get_current_user(SimpleNamespace(credentials=token))
        logger.debug(f'paylaod: {payload}')
        if not payload:
            await websocket.close(code=1003)
            return


        info = ServerCommandInfoDataControl().take(server_name)
        logger.debug(f'server info by{server_name}: {info}')

        async def send_progress(output: str) -> None:
            logger.debug(f'send_progress: {output}')
            await websocket.send_text(output)

        async def wrap_up(code: int=1000) -> None:
            logger.debug(f'will wrap up with code: {code}')
            await websocket.close(code)
        
        data = await websocket.receive_text()
        logger.debug(f'received data: {data}')
        if (info.protocol.value == Protocol.CLI.value):
            await request_to_proceed_commend_on_cli( 
                                command_line=(info.path_of_run +  ' ' + data),
                                progressFn=send_progress,
                                wrapUpFn=wrap_up)
        else:
            logger.error(f'protocol {info.protocol} is not supported')
            await websocket.close(code=1008)

    except WebSocketDisconnect:
        logger.error('Client disconnected')
        await websocket.close()
    except HTTPException as e:
        logger.exception('HTTP error', e)
        if (e.status_code == 401):
            await websocket.close(code=1003)
        await websocket.close(code=1008)
    except Exception as e:
        logger.exception('Unexpected error', e)
        await websocket.close(code=1008)

@server_router.post("/{server_name}/turn_off", response_model=None, dependencies=[Depends(get_current_user)])
async def turn_off_server(server_name: str):
    await ServerMessageProducer().send(f"{server_name}:turn_off")
    return OK_RESULT

@server_router.post("/{server_name}/turn_on", response_model=None, dependencies=[Depends(get_current_user)])
async def turn_on_server(server_name: str):
    await ServerMessageProducer().send(f"{server_name}:turn_on")
    return OK_RESULT

@server_router.get("/{server_name}/status", response_model=None, dependencies=[Depends(get_current_user)])
async def status_power_of_the_server(server_name: str):
    server_status = ServerPowerStatusInfoDataControl().take(server_name)
    return {
        "server_name": server_status.server_name,
        "power_status": server_status.power_status.name
    }
