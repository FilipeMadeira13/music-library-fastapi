from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.artist import ArtistCreateUpdate
from app.utils.validate_name import validate_name
from tests.conftest import seed_artist


def test_accepts_valid_name():
    result = validate_name("Rush")
    assert result == "Rush"


def test_rejects_empty_name():
    with pytest.raises(ValueError):
        validate_name("")


def test_rejects_empty_spaces_name():
    with pytest.raises(ValueError):
        validate_name("   ")


def test_rejects_missing_name():
    with pytest.raises(ValidationError):
        ArtistCreateUpdate.model_validate({})


def test_model_rejects_whitespace_name():
    with pytest.raises(ValidationError):
        ArtistCreateUpdate.model_validate({"name": "   "})


def test_model_rejects_empty_name():
    with pytest.raises(ValidationError):
        ArtistCreateUpdate.model_validate({"name": ""})


def test_model_accepts_valid_name():
    artist = ArtistCreateUpdate.model_validate({"name": "Rush"})
    assert artist.name == "Rush"


def test_database_starts_empty(database):
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()

    assert rows == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": ""},
        {"name": " "},
        {"name": None},
        {"name": "\t\n"},
    ],
)
def test_api_rejects_invalid_name(client, database, payload):
    response = client.post("/api/artists/", json=payload)
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert rows == []
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "name"]


def test_api_accepts_valid_name(client, database):
    response = client.post("/api/artists/", json={"name": "Rush"})
    with database.connect() as connection:
        rows = connection.execute("SELECT name FROM artists").fetchall()

    assert response.status_code == 201
    assert rows == [("Rush",)]


def test_api_lists_all_artists_with_basic_data(client, database):
    expected = [
        {
            "id": 10,
            "name": "Rush",
            "country": "Canada",
            "formation_year": 1968,
        },
        {
            "id": 20,
            "name": "Queen",
            "country": "United Kingdom",
            "formation_year": 1970,
        },
        {
            "id": 30,
            "name": "Independent artist",
            "country": None,
            "formation_year": None,
        },
    ]

    with database.connect() as connection:
        connection.executemany(
            """
            INSERT INTO artists (id, name, country, formation_year)
            VALUES (:id, :name, :country, :formation_year)
            """,
            expected,
        )

    response = client.get("/api/artists/")

    assert response.status_code == 200

    artists = response.json()
    assert isinstance(artists, list)
    assert len(artists) == len(expected)

    basic_data = [{field: artist[field] for field in expected[0]} for artist in artists]
    assert sorted(basic_data, key=lambda artist: artist["id"]) == expected


def test_api_lists_empty_artists(client):
    response = client.get("/api/artists/")

    assert response.status_code == 200
    assert response.json() == []


def test_api_creates_artist_with_optional_fields(client, database):
    payload = {
        "name": "Rush",
        "country": "Canada",
        "formation_year": 1968,
    }

    response = client.post("/api/artists/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Rush"
    assert body["country"] == "Canada"
    assert body["formation_year"] == 1968
    assert body["created_at"]
    assert body["updated_at"]

    with database.connect() as connection:
        rows = connection.execute(
            "SELECT name, country, formation_year FROM artists"
        ).fetchall()

    assert rows == [("Rush", "Canada", 1968)]


def test_api_rejects_future_formation_year_on_create(client, database):
    payload = {
        "name": "Rush",
        "formation_year": datetime.now().year + 1,
    }

    response = client.post("/api/artists/", json=payload)
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()

    assert response.status_code == 422
    assert rows == []
    errors = response.json()["detail"]
    assert errors[0]["loc"] == ["body", "formation_year"]


def test_api_gets_artist_by_id(client, database):
    artist_id = seed_artist(
        database,
        name="Rush",
        country="Canada",
        formation_year=1968,
    )

    response = client.get(f"/api/artists/{artist_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == artist_id
    assert body["name"] == "Rush"
    assert body["country"] == "Canada"
    assert body["formation_year"] == 1968
    assert body["created_at"]
    assert body["updated_at"]


def test_api_returns_404_when_artist_not_found(client):
    response = client.get("/api/artists/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found!"}


def test_api_updates_existing_artist(client, database):
    artist_id = seed_artist(
        database,
        name="Rush",
        country="Canada",
        formation_year=1968,
    )
    original = client.get(f"/api/artists/{artist_id}").json()

    response = client.put(
        f"/api/artists/{artist_id}",
        json={
            "name": "Geddy Lee",
            "country": "Canada",
            "formation_year": 1970,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == artist_id
    assert body["name"] == "Geddy Lee"
    assert body["country"] == "Canada"
    assert body["formation_year"] == 1970
    assert body["created_at"] == original["created_at"]
    assert body["updated_at"] != original["updated_at"]

    follow_up = client.get(f"/api/artists/{artist_id}")
    assert follow_up.json()["name"] == "Geddy Lee"
    assert follow_up.json()["formation_year"] == 1970


def test_api_returns_404_when_updating_missing_artist(client, database):
    response = client.put(
        "/api/artists/999",
        json={"name": "Rush", "country": "Canada", "formation_year": 1968},
    )
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found!"}
    assert rows == []


def test_api_rejects_invalid_payload_on_update(client, database):
    artist_id = seed_artist(database, name="Rush")

    response = client.put(f"/api/artists/{artist_id}", json={"name": "   "})
    with database.connect() as connection:
        rows = connection.execute("SELECT name FROM artists").fetchall()

    assert response.status_code == 422
    assert rows == [("Rush",)]
    errors = response.json()["detail"]
    assert errors[0]["loc"] == ["body", "name"]


def test_api_rejects_future_formation_year_on_update(client, database):
    artist_id = seed_artist(database, name="Rush", formation_year=1968)

    response = client.put(
        f"/api/artists/{artist_id}",
        json={"name": "Rush", "formation_year": datetime.now().year + 1},
    )
    with database.connect() as connection:
        rows = connection.execute("SELECT formation_year FROM artists").fetchall()

    assert response.status_code == 422
    assert rows == [(1968,)]
    errors = response.json()["detail"]
    assert errors[0]["loc"] == ["body", "formation_year"]


def test_api_deletes_existing_artist(client, database):
    artist_id = seed_artist(database, name="Rush")

    response = client.delete(f"/api/artists/{artist_id}")

    assert response.status_code == 204
    assert response.content == b""

    follow_up = client.get(f"/api/artists/{artist_id}")
    assert follow_up.status_code == 404

    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()
    assert rows == []


def test_api_returns_404_when_deleting_missing_artist(client, database):
    response = client.delete("/api/artists/999")
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found!"}
    assert rows == []
