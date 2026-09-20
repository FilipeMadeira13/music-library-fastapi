from typing import Optional

from app.database.local import LocalDatabase
from app.models.album import Album, AlbumCreateUpdate


class AlbumRepository:
    def __init__(self, database: LocalDatabase):
        self.db = database

    async def register_album(self, album: AlbumCreateUpdate) -> Optional[Album]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO albums (title, artist_id, release_year, genre, number_of_tracks) VALUES (?, ?, ?, ?, ?)",
                (album.title, album.artist_id, album.release_year, album.genre, album.number_of_tracks),
            )

        # Continuar