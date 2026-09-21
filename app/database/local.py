from contextlib import contextmanager
import sqlite3


class LocalDatabase:
    def __init__(self, file_name="music_library.db"):
        self.file_name = file_name
        self.start_db()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.file_name)
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    def start_db(self):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS artists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        country TEXT,
                        formation_year INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER NOT NULL,
                release_year INTEGER,
                genre TEXT,
                number_of_tracks INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artist_id) REFERENCES artists(id)
            )
        """)

        print("Banco de dados inicializado")
