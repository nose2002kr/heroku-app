from fastapi import APIRouter,       \
                    WebSocket,       \
                    WebSocketDisconnect,\
                    HTTPException
from route.login import get_current_user
from types import SimpleNamespace
from data_control import ServerCommandInfoDataControl
from server_command_info import Protocol
from service.server_cli import request_to_proceed_commend_on_cli

import asyncio
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
        #print('token: ' + token)
        payload = await get_current_user(SimpleNamespace(credentials=token))
        #print('payload: ' + payload)
        if not payload:
            await websocket.close(code=1003)
            return


        info = ServerCommandInfoDataControl.get_server_command_info(server_name)

        async def send_progress(output: str) -> None:
            #print('will send ' + output)
            await websocket.send_text(output)

        async def wrap_up(code: int=1000) -> None:
            #print('will wrap up')
            await websocket.close(code)
        
        data = await websocket.receive_text()
        if (info.protocol == Protocol.CLI):
            await request_to_proceed_commend_on_cli( 
                                command_line=(info.path_of_run +  ' ' + data),
                                progressFn=send_progress,
                                wrapUpFn=wrap_up)

    except WebSocketDisconnect:
        print("Client disconnected")
        await websocket.close()
    except HTTPException as e:
        print(f"HTTP error: {e}")
        if (e.status_code == 401):
            await websocket.close(code=1003)
        await websocket.close(code=1008)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.close(code=1008)
