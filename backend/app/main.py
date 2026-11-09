from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import Base, engine
from .routes import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # Phase 1 only; Alembic migrations come later
    yield


app = FastAPI(title="SYNTRA AI", version="0.1.0", lifespan=lifespan)
app.include_router(auth.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "syntra-backend", "version": app.version}


_frontend = Path(settings.frontend_dir)
if _frontend.is_dir():
    app.mount("/", StaticFiles(directory=_frontend, html=True), name="frontend")
