from typing import Optional

from app.database.local import LocalDatabase
from app.models.artist import Artist, ArtistCreateUpdate


class ArtistRepository:
    def __init__(self, database: LocalDatabase):
        self.db = database

    async def list_artists(self) -> list[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, country, formation_year FROM artists")
            lines = cursor.fetchall()
            artists = [
                Artist(
                    id=line[0],
                    name=line[1],
                    country=line[2],
                    formation_year=line[3],
                )
                for line in lines
            ]
            return artists

    async def register_artist(self, artist: ArtistCreateUpdate) -> Optional[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO artists (name, country, formation_year) VALUES (?, ?, ?)",
                (artist.name, artist.country, artist.formation_year),
            )
            artist_id = cursor.lastrowid
            if artist_id:
                return Artist(
                    id=artist_id,
                    name=artist.name,
                    country=artist.country,
                    formation_year=artist.formation_year,
                )
            return None
