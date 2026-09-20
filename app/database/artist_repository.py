from datetime import datetime, timezone
from typing import Optional

from app.database.local import LocalDatabase
from app.models.artist import Artist, ArtistCreateUpdate


class ArtistRepository:
    def __init__(self, database: LocalDatabase):
        self.db = database

    async def list_artists(self) -> list[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, name, country, formation_year, created_at, updated_at FROM artists"
            )
            lines = cursor.fetchall()
            artists = [
                Artist(
                    id=line[0],
                    name=line[1],
                    country=line[2],
                    formation_year=line[3],
                    created_at=line[4],
                    updated_at=line[5],
                )
                for line in lines
            ]
            return artists

    async def search_artist(self, artist_id: int) -> Optional[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, name, country, formation_year, created_at, updated_at FROM artists WHERE id = ?",
                (artist_id,),
            )
            line = cursor.fetchone()
            if line:
                return Artist(
                    id=line[0],
                    name=line[1],
                    country=line[2],
                    formation_year=line[3],
                    created_at=line[4],
                    updated_at=line[5],
                )

            return None

    async def register_artist(self, artist: ArtistCreateUpdate) -> Optional[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO artists (name, country, formation_year) VALUES (?, ?, ?)",
                (artist.name, artist.country, artist.formation_year),
            )
            artist_id = cursor.lastrowid
            if artist_id:
                cursor.execute(
                    "SELECT created_at, updated_at FROM artists WHERE id = ?",
                    (artist_id,),
                )
                line = cursor.fetchone()
                return Artist(
                    id=artist_id,
                    name=artist.name,
                    country=artist.country,
                    formation_year=artist.formation_year,
                    created_at=line[0],
                    updated_at=line[1],
                )
            return None

    async def update_artist(
        self, artist_id: int, artist: ArtistCreateUpdate
    ) -> Optional[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE artists SET name = ?, country = ?, formation_year = ?, updated_at = ? WHERE id = ?",
                (
                    artist.name,
                    artist.country,
                    artist.formation_year,
                    datetime.now(timezone.utc),
                    artist_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
            cursor.execute(
                "SELECT created_at, updated_at FROM artists WHERE id = ?",
                (artist_id,),
            )
            line = cursor.fetchone()
            return Artist(
                id=artist_id,
                name=artist.name,
                country=artist.country,
                formation_year=artist.formation_year,
                created_at=line[0],
                updated_at=line[1],
            )

    async def delete_artist(self, artist_id: int) -> bool:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
            return cursor.rowcount > 0
