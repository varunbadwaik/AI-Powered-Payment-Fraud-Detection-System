"""
WebSocket connection manager for real-time fraud alert streaming.

Provides bidirectional communication between the backend prediction
engine and connected dashboard clients, eliminating polling latency.
"""

import json
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections and broadcasts
    prediction results to all connected dashboard clients.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        """
        Broadcast a prediction result to ALL connected clients.
        Gracefully handles disconnected clients.
        """
        # Serialize datetimes for JSON
        serializable = _make_serializable(data)
        message = json.dumps(serializable)

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Cleanup dead connections
        for conn in disconnected:
            self.disconnect(conn)


def _make_serializable(obj: Any) -> Any:
    """Convert non-serializable types (datetime, etc.) for JSON."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(i) for i in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


# Module-level singleton
ws_manager = ConnectionManager()
