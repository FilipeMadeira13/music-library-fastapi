import pytest
from pydantic import ValidationError

from app.models.artist import ArtistCreateUpdate
from app.utils.validate_name import validate_name


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
            "name": "Artista independente",
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
