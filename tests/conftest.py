import pytest

from app.database.local import LocalDatabase


@pytest.fixture
def database(tmp_path):
    return LocalDatabase(tmp_path / "test_music_library.db")
