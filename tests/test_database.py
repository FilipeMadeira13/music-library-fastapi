from pathlib import Path
import sqlite3

import pytest

from tests.conftest import seed_album, seed_artist


def test_local_database_creates_expected_tables(database):
    with database.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        artist_count = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
        album_count = connection.execute("SELECT COUNT(*) FROM albums").fetchone()[0]

    assert "artists" in tables
    assert "albums" in tables
    assert artist_count == 0
    assert album_count == 0


def test_database_file_lives_in_tmp_path(database, tmp_path):
    assert Path(database.file_name).parent == tmp_path
    assert Path(database.file_name).name == "test_music_library.db"


def test_deleting_artist_with_albums_block_operations(client, database):
    artist_id = seed_artist(database, name="Rush")
    seed_album(database, title="2112", artist_id=artist_id)

    response = client.delete(f"/api/artists/{artist_id}")

    assert response.status_code == 409
    with database.connect() as connection:
        albums = connection.execute("SELECT title, artist_id FROM albums").fetchall()

    assert albums == [("2112", artist_id)]


def test_sql_delete_blocks_artist_with_albums(database):
    artist_id = seed_artist(database, name="Rush")
    album_id = seed_album(database, title="2112", artist_id=artist_id)

    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        with database.connect() as connection:
            connection.execute(
                "DELETE FROM artists WHERE id = ?",
                (artist_id,),
            )

    with database.connect() as connection:
        artist = connection.execute(
            "SELECT id FROM artists WHERE id = ?", (artist_id,)
        ).fetchone()
        album = connection.execute(
            "SELECT artist_id FROM albums WHERE id = ?", (album_id,)
        ).fetchone()

    assert artist == (artist_id,)
    assert album == (album_id,)
