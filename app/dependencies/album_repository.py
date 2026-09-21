from typing import Annotated

from fastapi import Depends

from app.database.album_repository import AlbumRepository
from app.database.local import LocalDatabase
from app.dependencies.main import get_database


def get_album_repository(
    local_database: Annotated[LocalDatabase, Depends(get_database)],
) -> AlbumRepository:
    return AlbumRepository(local_database)
