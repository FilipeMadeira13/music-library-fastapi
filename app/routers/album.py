from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.database.album_repository import AlbumRepository
from app.database.artist_repository import ArtistRepository
from app.dependencies.album_repository import get_album_repository
from app.dependencies.artist_repository import get_artist_repository
from app.models.album import Album, AlbumCreateUpdate

router = APIRouter(prefix="/api/albums")


@router.get("/", response_model=list[Album], tags=["Album"])
async def list_albums(
    album_repository: Annotated[AlbumRepository, Depends(get_album_repository)],
):
    return await album_repository.list_albums()


@router.post("/", response_model=Album, status_code=201, tags=["Album"])
async def register_album(
    album_repository: Annotated[AlbumRepository, Depends(get_album_repository)],
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
    album: AlbumCreateUpdate,
):
    artist = await artist_repository.search_artist(album.artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artista não encontrado!")
    return await album_repository.register_album(album)
