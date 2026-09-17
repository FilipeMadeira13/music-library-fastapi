from contextlib import contextmanager
import sqlite3

class LocalDatabase():
    def __init__(self, file_name='music_library.db'):
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
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS artists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        country TEXT,
                        formation_year INT
                    )
                """
            )

        print('Banco de dados inicializado')