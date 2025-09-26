from __future__ import annotations
from fastapi import FastAPI
from .api.routes import calls as calls_routes
from .api.routes import recordings as rec_routes

app = FastAPI(title="Calls Service")
app.include_router(calls_routes.router)
app.include_router(rec_routes.router)
