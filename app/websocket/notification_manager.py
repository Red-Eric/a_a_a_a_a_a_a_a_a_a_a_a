from fastapi import WebSocket
from typing import Dict, List

class NotificationManager:
    def __init__(self):
        # Dictionnaire qui mappe chaque établissement à une liste de connexions WebSocket
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, etablissement_id: int):
        await websocket.accept()
        if etablissement_id not in self.active_connections:
            self.active_connections[etablissement_id] = []
        self.active_connections[etablissement_id].append(websocket)

    def disconnect(self, websocket: WebSocket):
        # Retirer la connexion WebSocket de tous les établissements
        for etab_id, connections in list(self.active_connections.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.active_connections[etab_id]
                break

    async def send_to_etablissement(self, etablissement_id: int, event: str, payload: dict):
        message = {"event": event, "payload": payload}
        connections = self.active_connections.get(etablissement_id, [])
        for connection in connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

    async def broadcast(self, event: str, payload: dict):
        # Envoie à tous les établissements
        message = {"event": event, "payload": payload}
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except:
                    self.disconnect(connection)


# Instance globale
notification_manager = NotificationManager()
