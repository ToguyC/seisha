from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .routes.archers import router as archers_router
from .routes.arrows import router as arrows_router
from .routes.matches import router as matches_router
from .routes.series import router as series_router
from .routes.teams import router as teams_router
from .routes.tournaments import router as tournaments_router
from .routes.websocket import router as websocket_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(archers_router)
app.include_router(tournaments_router)
app.include_router(matches_router)
app.include_router(series_router)
app.include_router(arrows_router)
app.include_router(teams_router)
app.include_router(websocket_router)
