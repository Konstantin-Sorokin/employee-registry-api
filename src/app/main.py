from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core import settings
from app.core.config import UPLOAD_DIR
from app.routers import employees_web_router

app = FastAPI()

app.include_router(employees_web_router)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads/photos", StaticFiles(directory=str(UPLOAD_DIR)), name="photos")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
