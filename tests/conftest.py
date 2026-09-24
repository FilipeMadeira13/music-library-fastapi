import pytest
from fastapi.testclient import TestClient

from app.database.local import LocalDatabase


@pytest.fixture
def database(tmp_path):
    return LocalDatabase(tmp_path / "test_music_library.db")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
