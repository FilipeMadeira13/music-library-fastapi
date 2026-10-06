from fastapi import FastAPI

from app.routers import album, artist

app = FastAPI(
    title="Music Library",
    description="Music library management application.",
    version="1.0.0",
)

app.include_router(artist.router)
app.include_router(album.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Checks if the API is live."""
    return {"status": "OK"}
