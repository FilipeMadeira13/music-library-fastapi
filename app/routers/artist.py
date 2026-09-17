from typing import Annotated

from fastapi import APIRouter, Depends

from app.database.artist_repository import ArtistRepository
from app.dependencies.artist_repository import get_artist_repository
from app.models.artist import Artist, ArtistCreateUpdate

router = APIRouter(prefix="/api/artists")


@router.get("/", response_model=list[Artist], tags=['Artist'])
async def list_artists(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
):
    return await artist_repository.list_artists()


@router.post("/", response_model=Artist, status_code=201, tags=['Artist'])
async def register_artist(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
    artist: ArtistCreateUpdate,
):
    return await artist_repository.register_artist(artist)
