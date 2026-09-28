from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.artist import ArtistCreateUpdate
from app.utils.validate_year import validate_year


def test_accepts_missing_year():
    assert validate_year(None) is None


def test_accepts_current_year():
    current_year = datetime.now().year
    assert validate_year(current_year) == current_year


def test_accepts_past_year():
    assert validate_year(1968) == 1968


def test_rejects_future_year():
    with pytest.raises(ValueError):
        validate_year(datetime.now().year + 1)


def test_model_accepts_valid_formation_year():
    artist = ArtistCreateUpdate.model_validate(
        {"name": "Rush", "formation_year": 1968}
    )
    assert artist.formation_year == 1968


def test_model_rejects_future_formation_year():
    with pytest.raises(ValidationError):
        ArtistCreateUpdate.model_validate(
            {"name": "Rush", "formation_year": datetime.now().year + 1}
        )
