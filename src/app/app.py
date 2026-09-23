"""Acquisition Risk Cockpit — FastAPI entry point.

Analytical reads (Overview, Risk Queue, Contract Detail) come from the Gold
table via a SQL warehouse; operational writes (assignment, status, notes) go to
the Lakebase action queue. The built React frontend is served from ./frontend/dist.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.config import CATALOG, SCHEMA
from server.db import LAKEBASE_ENABLED, init_schema, pool
from server.routes import actions, contracts, overview


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open the Lakebase pool (if configured) and ensure the cockpit schema exists.
    if pool is not None:
        pool.open(wait=True, timeout=30.0)
        init_schema()
    yield
    if pool is not None:
        pool.close()


app = FastAPI(title="Acquisition Risk Cockpit", lifespan=lifespan)

app.include_router(overview.router, prefix="/api")
app.include_router(contracts.router, prefix="/api")
app.include_router(actions.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    """Liveness plus the analytical target and whether Lakebase writes are wired."""
    return {
        "status": "ok",
        "catalog": CATALOG,
        "schema": SCHEMA,
        "lakebase_enabled": LAKEBASE_ENABLED,
    }


# --- Serve the built React SPA ------------------------------------------------

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(_FRONTEND_DIR):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(_FRONTEND_DIR, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))
