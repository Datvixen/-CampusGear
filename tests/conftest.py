import pytest

import app as campusgear


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setattr(campusgear, "DB", tmp_path / "campusgear-test.db")
    campusgear.init_db()


@pytest.fixture
def client():
    return campusgear.app.test_client()