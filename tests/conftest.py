import pytest
from fastapi.testclient import TestClient

from app.database.local import LocalDatabase


@pytest.fixture
def database(tmp_path):
    return LocalDatabase(tmp_path / "test_music_library.db")


@pytest.fixture
def client(database, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from app.dependencies.main import get_database
    from app.main import app

    def get_test_database():
        return database

    monkeypatch.setitem(
        app.dependency_overrides,
        get_database,
        get_test_database,
    )

    with TestClient(app) as test_client:
        yield test_client


def seed_artist(
    database,
    *,
    artist_id=None,
    name="Rush",
    country=None,
    formation_year=None,
):
    with database.connect() as connection:
        if artist_id is None:
            cursor = connection.execute(
                """
                INSERT INTO artists (name, country, formation_year)
                VALUES (?, ?, ?)
                """,
                (name, country, formation_year),
            )
            return cursor.lastrowid

        connection.execute(
            """
            INSERT INTO artists (id, name, country, formation_year)
            VALUES (?, ?, ?, ?)
            """,
            (artist_id, name, country, formation_year),
        )
        return artist_id


def seed_album(
    database,
    *,
    album_id=None,
    title="2112",
    artist_id,
    release_year=None,
    genre=None,
    number_of_tracks=None,
):
    with database.connect() as connection:
        if album_id is None:
            cursor = connection.execute(
                """
                INSERT INTO albums (
                    title, artist_id, release_year, genre, number_of_tracks
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, artist_id, release_year, genre, number_of_tracks),
            )
            return cursor.lastrowid

        connection.execute(
            """
            INSERT INTO albums (
                id, title, artist_id, release_year, genre, number_of_tracks
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (album_id, title, artist_id, release_year, genre, number_of_tracks),
        )
        return album_id
