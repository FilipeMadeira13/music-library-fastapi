from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.album import AlbumCreateUpdate
from tests.conftest import seed_album, seed_artist


def test_api_lists_empty_albums(client):
    response = client.get("/api/albums/")

    assert response.status_code == 200
    assert response.json() == []


def test_api_lists_all_albums_with_basic_data(client, database):
    seed_artist(database, artist_id=10, name="Rush")
    seed_artist(database, artist_id=20, name="Queen")

    expected = [
        {
            "id": 1,
            "title": "2112",
            "artist_id": 10,
            "release_year": 1976,
            "genre": "Progressive rock",
            "number_of_tracks": 6,
        },
        {
            "id": 2,
            "title": "A Night at the Opera",
            "artist_id": 20,
            "release_year": 1975,
            "genre": "Rock",
            "number_of_tracks": 12,
        },
        {
            "id": 3,
            "title": "Demo",
            "artist_id": 10,
            "release_year": None,
            "genre": None,
            "number_of_tracks": None,
        },
    ]

    for album in expected:
        seed_album(
            database,
            album_id=album["id"],
            title=album["title"],
            artist_id=album["artist_id"],
            release_year=album["release_year"],
            genre=album["genre"],
            number_of_tracks=album["number_of_tracks"],
        )

    response = client.get("/api/albums/")

    assert response.status_code == 200
    albums = response.json()
    assert isinstance(albums, list)
    assert len(albums) == len(expected)

    basic_data = [{field: album[field] for field in expected[0]} for album in albums]
    assert sorted(basic_data, key=lambda album: album["id"]) == expected


def test_api_creates_album_for_existing_artist(client, database):
    artist_id = seed_artist(database, name="Rush")
    payload = {
        "title": "2112",
        "artist_id": artist_id,
        "release_year": 1976,
        "genre": "Progressive rock",
        "number_of_tracks": 6,
    }

    response = client.post("/api/albums/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "2112"
    assert body["artist_id"] == artist_id
    assert body["release_year"] == 1976
    assert body["genre"] == "Progressive rock"
    assert body["number_of_tracks"] == 6
    assert body["created_at"]
    assert body["updated_at"]

    with database.connect() as connection:
        rows = connection.execute("""
            SELECT title, artist_id, release_year, genre, number_of_tracks
            FROM albums
            """).fetchall()

    assert rows == [("2112", artist_id, 1976, "Progressive rock", 6)]


def test_api_returns_422_when_creating_album_for_missing_artist(client, database):
    payload = {
        "title": "2112",
        "artist_id": 999,
        "release_year": 1976,
        "genre": "Progressive rock",
        "number_of_tracks": 6,
    }

    response = client.post("/api/albums/", json=payload)
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM albums").fetchall()

    assert response.status_code == 422
    assert response.json() == {"detail": "The informed artist does not exist."}
    assert rows == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "2112"},
        {"artist_id": 1},
        {"title": "2112", "artist_id": 1, "number_of_tracks": 0},
        {"title": "2112", "artist_id": 1, "number_of_tracks": -1},
        {"title": "2112", "artist_id": 1, "number_of_tracks": "six"},
    ],
)
def test_api_rejects_invalid_album_payload(client, database, payload):
    seed_artist(database, artist_id=1, name="Rush")

    response = client.post("/api/albums/", json=payload)
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM albums").fetchall()

    assert response.status_code == 422
    assert rows == []


def test_create_model_rejects_future_release_year():
    future_year = datetime.now().year + 1
    with pytest.raises(ValidationError) as exc_info:
        AlbumCreateUpdate.model_validate(
            {
                "title": "Unreleased",
                "artist_id": 1,
                "release_year": future_year,
            }
        )

    assert exc_info.value.errors()[0]["loc"] == ("release_year",)


def test_api_rejects_future_release_year_without_saving_album(client, database):
    artist_id = seed_artist(database, name="Rush")
    future_year = datetime.now().year + 1

    response = client.post(
        "/api/albums/",
        json={
            "title": "Unreleased",
            "artist_id": artist_id,
            "release_year": future_year,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "release_year"]

    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM albums").fetchall()

    assert rows == []


def test_api_gets_album_by_id(client, database):
    rush_id = seed_artist(database, artist_id=10, name="Rush")
    queen_id = seed_artist(database, artist_id=20, name="Queen")
    seed_album(
        database,
        album_id=1,
        title="A Farewell to Kings",
        artist_id=rush_id,
        release_year=1977,
        genre="Progressive rock",
        number_of_tracks=6,
    )
    requested_album_id = seed_album(
        database,
        album_id=2,
        title="2112",
        artist_id=rush_id,
        release_year=1976,
        genre="Progressive rock",
        number_of_tracks=6,
    )
    seed_album(
        database,
        album_id=3,
        title="A Night at the Opera",
        artist_id=queen_id,
        release_year=1975,
        genre="Rock",
        number_of_tracks=12,
    )

    response = client.get(f"/api/albums/{requested_album_id}")

    assert response.status_code == 200
    body = response.json()
    assert {
        "id": body["id"],
        "title": body["title"],
        "artist_id": body["artist_id"],
        "artist_name": body["artist_name"],
        "release_year": body["release_year"],
        "genre": body["genre"],
        "number_of_tracks": body["number_of_tracks"],
    } == {
        "id": requested_album_id,
        "title": "2112",
        "artist_id": rush_id,
        "artist_name": "Rush",
        "release_year": 1976,
        "genre": "Progressive rock",
        "number_of_tracks": 6,
    }
    assert body["created_at"]
    assert body["updated_at"]


def test_api_returns_404_when_album_not_found(client):
    response = client.get("/api/albums/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found!"}


def test_api_search_album_preserves_null_fields(client, database):
    artist_id = seed_artist(database, name="Rush")
    album_id = seed_album(database, title="Demo", artist_id=artist_id)

    response = client.get(f"/api/albums/{album_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == album_id
    assert body["release_year"] is None
    assert body["genre"] is None
    assert body["number_of_tracks"] is None


def test_api_updates_album_and_artist(client, database):
    original_artist = seed_artist(database, name="Rush")
    new_artist = seed_artist(database, name="Queen")
    album_id = seed_album(database, artist_id=original_artist)
    before = client.get(f"/api/albums/{album_id}").json()
    payload = {
        "title": "A Night at the Opera",
        "artist_id": new_artist,
        "release_year": 1975,
        "genre": "Rock",
        "number_of_tracks": 12,
    }

    response = client.put(f"/api/albums/{album_id}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert all(body[key] == value for key, value in payload.items())
    assert body["artist_name"] == "Queen"
    assert body["created_at"] == before["created_at"]
    assert body["updated_at"] != before["updated_at"]
    assert client.get(f"/api/albums/{album_id}").json() == body


def test_api_update_rejects_missing_artist_without_changing_album(client, database):
    artist_id = seed_artist(database)
    album_id = seed_album(database, artist_id=artist_id)
    before = client.get(f"/api/albums/{album_id}").json()

    response = client.put(
        f"/api/albums/{album_id}",
        json={"title": "Changed", "artist_id": 999},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "The informed artist does not exist."}
    assert client.get(f"/api/albums/{album_id}").json() == before


def test_api_update_returns_404_for_missing_album(client, database):
    artist_id = seed_artist(database)
    response = client.put(
        "/api/albums/999", json={"title": "Demo", "artist_id": artist_id}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found!"}


def test_api_update_clears_optional_fields(client, database):
    artist_id = seed_artist(database)
    album_id = seed_album(
        database,
        artist_id=artist_id,
        release_year=1976,
        genre="Rock",
        number_of_tracks=6,
    )

    response = client.put(
        f"/api/albums/{album_id}", json={"title": "Demo", "artist_id": artist_id}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["release_year"] is None
    assert body["genre"] is None
    assert body["number_of_tracks"] is None
    assert client.get(f"/api/albums/{album_id}").json() == body


def test_api_deletes_existing_album(client, database):
    artist_id = seed_artist(database)
    album_id = seed_album(database, artist_id=artist_id)
    remaining_album_id = seed_album(
        database,
        title="Signals",
        artist_id=artist_id,
    )

    response = client.delete(f"/api/albums/{album_id}")

    assert response.status_code == 204
    assert response.content == b""

    follow_up = client.get(f"/api/albums/{album_id}")
    assert follow_up.status_code == 404

    with database.connect() as connection:
        rows = connection.execute("SELECT id FROM albums").fetchall()
    assert rows == [(remaining_album_id,)]
