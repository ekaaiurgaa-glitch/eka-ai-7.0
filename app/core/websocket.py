"""WebSocket support for real-time updates."""
from fastapi import WebSocket
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, tenant_id: str):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        logger.info(f"Client connected to tenant {tenant_id}")
    
    def disconnect(self, websocket: WebSocket, tenant_id: str):
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
    
    async def broadcast_to_tenant(self, message: dict, tenant_id: str):
        if tenant_id not in self.active_connections:
            return
        for connection in list(self.active_connections[tenant_id]):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection, tenant_id)


manager = ConnectionManager()


async def notify_job_update(job_id: int, state: str, tenant_id: str):
    await manager.broadcast_to_tenant({"type": "job_update", "job_id": job_id, "state": state}, tenant_id)
