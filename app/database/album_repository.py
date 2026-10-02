import sqlite3
from typing import Optional

from app.database.local import LocalDatabase
from app.exceptions import AlbumArtistNotFoundError
from app.models.album import Album, AlbumCreateUpdate


class AlbumRepository:
    def __init__(self, database: LocalDatabase):
        self.db = database

    async def list_albums(self):
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                    SELECT
                        a.id, a.title, a.artist_id, ar.name AS artist_name,
                        a.release_year,
                        a.genre, a.number_of_tracks, a.created_at, a.updated_at
                    FROM albums AS a
                    JOIN artists AS ar ON ar.id = a.artist_id
                """)
            lines = cursor.fetchall()
            albums = [
                Album(
                    id=line[0],
                    title=line[1],
                    artist_id=line[2],
                    artist_name=line[3],
                    release_year=line[4],
                    genre=line[5],
                    number_of_tracks=line[6],
                    created_at=line[7],
                    updated_at=line[8],
                )
                for line in lines
            ]
            return albums

    async def register_album(self, album: AlbumCreateUpdate) -> Optional[Album]:
        try:
            with self.db.connect() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO albums (title, artist_id, release_year, genre, number_of_tracks) VALUES (?, ?, ?, ?, ?)",
                    (
                        album.title,
                        album.artist_id,
                        album.release_year,
                        album.genre,
                        album.number_of_tracks,
                    ),
                )
                album_id = cursor.lastrowid
                if album_id:
                    cursor.execute(
                        "SELECT created_at, updated_at FROM albums WHERE id = ?",
                        (album_id,),
                    )
                    line = cursor.fetchone()
                    return Album(
                        id=album_id,
                        title=album.title,
                        artist_id=album.artist_id,
                        release_year=album.release_year,
                        genre=album.genre,
                        number_of_tracks=album.number_of_tracks,
                        created_at=line[0],
                        updated_at=line[1],
                    )
        except sqlite3.IntegrityError as exc:
            if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY:
                raise AlbumArtistNotFoundError(album.artist_id) from exc
            raise
