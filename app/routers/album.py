from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.database.album_repository import AlbumRepository
from app.database.artist_repository import ArtistRepository
from app.dependencies.album_repository import get_album_repository
from app.dependencies.artist_repository import get_artist_repository
from app.exceptions import AlbumArtistNotFoundError
from app.models.album import Album, AlbumCreateUpdate

router = APIRouter(prefix="/api/albums")


@router.get("/", response_model=list[Album], tags=["Album"])
async def list_albums(
    album_repository: Annotated[
        AlbumRepository,
        Depends(get_album_repository),
    ],
):
    return await album_repository.list_albums()


@router.get("/{album_id}", response_model=Optional[Album], tags=["Album"])
async def search_album(
    album_repository: Annotated[
        AlbumRepository,
        Depends(get_album_repository),
    ],
    album_id: str,
):
    album = await album_repository.search_album(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found!")
    return album


@router.post("/", response_model=Album, status_code=201, tags=["Album"])
async def register_album(
    album_repository: Annotated[AlbumRepository, Depends(get_album_repository)],
    album: AlbumCreateUpdate,
):
    try:
        return await album_repository.register_album(album)
    except AlbumArtistNotFoundError as exc:
        raise HTTPException(
            status_code=422,
            detail="The informed artist does not exist.",
        ) from exc
