import asyncio
import json
import logging

import websockets


logger = logging.getLogger(__name__)
ClientSet = set[websockets.ServerConnection]


class StatusWebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: ClientSet = set()

    async def handler(self, websocket: websockets.ServerConnection) -> None:
        self.clients.add(websocket)
        logger.info("WebSocket Client verbunden")

        try:
            async for _ in websocket:
                pass
        finally:
            self.clients.remove(websocket)
            logger.info("WebSocket Client getrennt")

    async def broadcast(self, message: dict) -> None:
        if not self.clients:
            return

        payload = json.dumps(message)

        await asyncio.gather(
            *(client.send(payload) for client in self.clients),
            return_exceptions=True,
        )

    async def start(self) -> None:
        logger.info("WebSocket Server startet")

        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()
