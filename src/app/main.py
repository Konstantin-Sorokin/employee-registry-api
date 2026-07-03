import uvicorn
from fastapi import FastAPI

from app.core import settings
from app.routers import employees_router

app = FastAPI(prefix=settings.api.prefix)

app.include_router(employees_router)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
