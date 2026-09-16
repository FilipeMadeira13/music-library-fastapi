from fastapi import FastAPI

from app.routers import artist

app = FastAPI(
    title="Music Library",
    description="Aplicação para gerenciamento de biblioteca de música",
    version="1.0.0",
)

app.include_router(artist.router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Verifica se a API está no ar."""
    return {"status": "OK"}
