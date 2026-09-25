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


def test_api_rejects_missing_name(client, database):
    response = client.post("/api/artists/", json={})
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM artists").fetchall()

    assert response.status_code == 422
    assert rows == []
