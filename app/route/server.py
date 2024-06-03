from fastapi import APIRouter,       \
                    WebSocket,       \
                    WebSocketDisconnect
from route.login import get_current_user

server_router = APIRouter(prefix='/api/server')
OK_RESULT = {"message": "OK"}
OK_RESULT_RESPONSE_EXAMPLE = {200:{"content":
                               {"application/json":{"example":OK_RESULT}}
                             }}

@server_router.websocket("/{server_name}/prompt")
async def prompt_to_server(websocket: WebSocket, server_name: str):
    token = websocket.query_params.get('token')
    await websocket.accept()
    try:
        headers = websocket.headers
        print(token)
        #payload = get_current_user({'token':{'credentials':token}})
        # if not payload:
        #     await websocket.close(code=1008)
        #     return

        data = await websocket.receive_text()
        print(f"Message received: {data}")
        await websocket.send_text(f"Message from server: {data}")
        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")
