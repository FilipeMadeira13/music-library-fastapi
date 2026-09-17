from app.database.local import LocalDatabase
from app.models.artist import Artist


class ArtistRepository:
    def __init__(self, database: LocalDatabase):
        self.db = database

    async def list_artists(self) -> list[Artist]:
        with self.db.connect() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT id, name, country, formation_year FROM artists')
            lines = cursor.fetchall()
            artists = [Artist(
                id=line[0],
                name=line[1],
                country=line[2],
                formation_year=line[3],
            ) for line in lines]
            return artists