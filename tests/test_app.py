import pytest

import cosmos_client as cc
from app import create_app


class StubDB:
    def __init__(self):
        self._movies = []
        self._ratings = {}
        self._comments = {}

    # Movies
    def list_movies(self):
        return list(self._movies)

    def create_movie(self, title: str):
        mid = str(len(self._movies) + 1)
        item = {"id": mid, "title": title}
        self._movies.append(item)
        return item

    def get_movie(self, movie_id: str):
        return next((m for m in self._movies if m["id"] == movie_id), None)

    # Ratings
    def add_rating(self, movie_id: str, stars: int):
        self._ratings.setdefault(movie_id, []).append({"stars": stars})
        return {"ok": True}

    def list_ratings(self, movie_id: str):
        return self._ratings.get(movie_id, [])

    def average_rating(self, movie_id: str):
        lst = self._ratings.get(movie_id, [])
        if not lst:
            return None
        return round(sum(r["stars"] for r in lst) / len(lst), 2)

    # Comments
    def add_comment(self, movie_id: str, text: str):
        self._comments.setdefault(movie_id, []).append({"text": text})
        return {"ok": True}

    def list_comments(self, movie_id: str):
        return self._comments.get(movie_id, [])


@pytest.fixture(autouse=True)
def stub_cosmos(monkeypatch):
    # Replace the global singleton with a stub
    stub = StubDB()

    def fake_get_cosmos():
        return stub

    monkeypatch.setattr(cc, "get_cosmos", fake_get_cosmos)
    # Ensure no stale singleton
    if hasattr(cc, "_db_singleton"):
        monkeypatch.setattr(cc, "_db_singleton", None, raising=False)
    return stub


def test_index_shows_empty_list(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"No movies yet" in res.data


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_add_movie_and_rate_and_comment(client):
    # Add movie
    res = client.post(
        "/movies", data={"title": "Inception"}, follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Inception" in res.data

    # Get movie id by scraping the page link
    # For simplicity, we visit the first movie link pattern
    res = client.get("/")
    assert res.status_code == 200
    # crude parse to find /movies/1
    assert b"/movies/1" in res.data

    # Rate movie
    res = client.post(
        "/movies/1/rate", data={"stars": "5"}, follow_redirects=True
    )
    assert res.status_code == 200
    assert b"5 / 5" in res.data

    # Comment
    res = client.post(
        "/movies/1/comment", data={"text": "Great!"}, follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Great!" in res.data
