from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.database.artist_repository import ArtistRepository
from app.dependencies.artist_repository import get_artist_repository
from app.models.artist import Artist, ArtistCreateUpdate

router = APIRouter(prefix="/api/artists")


@router.get("/", response_model=list[Artist], tags=["Artist"])
async def list_artists(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
):
    return await artist_repository.list_artists()


@router.get("/{artist_id}", response_model=Optional[Artist], tags=["Artist"])
async def search_artist(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
    artist_id: int,
):
    artist = await artist_repository.search_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artista não encontrado!")
    return artist


@router.post("/", response_model=Artist, status_code=201, tags=["Artist"])
async def register_artist(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
    artist: ArtistCreateUpdate,
):
    return await artist_repository.register_artist(artist)
    if not artista:
        raise HTTPException(status_code=404, detail="Artista não encontrado!")
    return artista


@router.put("/{artist_id}", response_model=Optional[Artist])
async def update_artist(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
    artist_id: int,
    artist: ArtistCreateUpdate,
):
    updated_artist = await artist_repository.update_artist(
        artist_id=artist_id, artist=artist
    )
    if not updated_artist:
        raise HTTPException(status_code=404, detail="Artista não encontrado!")
    return updated_artist


@router.delete("/{artist_id}", status_code=204)
async def delete_artist(
    artist_repository: Annotated[ArtistRepository, Depends(get_artist_repository)],
    artist_id: int,
):
    success = await artist_repository.delete_artist(artist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Artista não encontrado!")
