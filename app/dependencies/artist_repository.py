from typing import Annotated

from fastapi import Depends

from app.database.artist_repository import ArtistRepository
from app.database.local import LocalDatabase
from app.dependencies.main import get_database


def get_artist_repository(
    local_database: Annotated[LocalDatabase, Depends(get_database)],
) -> ArtistRepository:
    return ArtistRepository(local_database)
