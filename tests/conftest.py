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
    from app.dependencies.main import get_database

    def get_test_database():
        return database

    monkeypatch.setitem(
        app.dependency_overrides,
        get_database,
        get_test_database,
    )

    with TestClient(app) as test_client:
        yield test_client
