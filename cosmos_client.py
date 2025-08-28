import os
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional

# Import exceptions with a safe fallback so we can catch specific errors
try:  # pragma: no cover - exercised in integration, not unit tests
    from azure.cosmos import exceptions as cosmos_exceptions  # type: ignore
except ImportError:  # pragma: no cover
    class cosmos_exceptions:  # type: ignore
        class CosmosHttpResponseError(Exception):
            pass

        class CosmosResourceNotFoundError(Exception):
            pass


DB_NAME = os.environ.get("COSMOS_DB_NAME", "vibemovie-db")
MOVIES_CONTAINER = os.environ.get("COSMOS_MOVIES_CONTAINER", "movies")
RATINGS_CONTAINER = os.environ.get("COSMOS_RATINGS_CONTAINER", "ratings")
COMMENTS_CONTAINER = os.environ.get("COSMOS_COMMENTS_CONTAINER", "comments")


class CosmosUnavailable(RuntimeError):
    pass


@dataclass
class Movie:
    id: str
    title: str


def _get_emulator_connection():
    # Defaults for Azure Cosmos DB Emulator for Linux/Windows
    # Endpoint and key can be overridden via environment variables if needed
    endpoint = os.environ.get("COSMOS_ENDPOINT", "https://localhost:8081/")
    key = os.environ.get(
        "COSMOS_KEY",
        # Default master key for local emulator
        "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9K0HB4Q==",
    )
    return endpoint, key


class DB:
    def __init__(self) -> None:
        endpoint, key = _get_emulator_connection()
        try:
            # Import azure.cosmos lazily so unit tests can run
            # without the package installed
            from azure.cosmos import CosmosClient, PartitionKey  # type: ignore

            # If using local emulator (self-signed), disable TLS verify for dev
            if any(h in endpoint for h in ("localhost", "127.0.0.1")):
                verify_env = os.environ.get(
                    "COSMOS_VERIFY_TLS", "false"
                ).lower()
                if verify_env not in ("1", "true", "yes", "on"):
                    os.environ.setdefault("PYTHONHTTPSVERIFY", "0")
            # Create the Cosmos client
            self.client: Any = CosmosClient(endpoint, key)
        except Exception as e:  # pragma: no cover  # noqa: BLE001
            raise CosmosUnavailable(
                "Failed to create CosmosClient. Ensure the emulator is "
                "running and certificates are trusted. Details: "
                f"{e}"
            ) from e

        try:
            # Database and containers (create if not exists)
            self.db: Any = self.client.create_database_if_not_exists(
                id=DB_NAME
            )
            self.movies: Any = self.db.create_container_if_not_exists(
                id=MOVIES_CONTAINER,
                partition_key=PartitionKey(path="/id"),
            )
            self.ratings: Any = self.db.create_container_if_not_exists(
                id=RATINGS_CONTAINER,
                partition_key=PartitionKey(path="/movieId"),
            )
            self.comments: Any = self.db.create_container_if_not_exists(
                id=COMMENTS_CONTAINER,
                partition_key=PartitionKey(path="/movieId"),
            )
        except Exception as e:  # noqa: BLE001
            raise CosmosUnavailable(
                "Could not connect to Cosmos DB. Is the local emulator "
                f"running? Details: {e}"
            ) from e

    # Movies
    def list_movies(self) -> List[Dict[str, Any]]:
        return list(self.movies.read_all_items())

    def create_movie(self, title: str) -> Dict[str, Any]:
        item = {"id": str(uuid.uuid4()), "title": title}
        return self.movies.create_item(body=item)

    def get_movie(self, movie_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.movies.read_item(item=movie_id, partition_key=movie_id)
        except (
            cosmos_exceptions.CosmosHttpResponseError,
            cosmos_exceptions.CosmosResourceNotFoundError,
        ):
            return None

    # Ratings
    def add_rating(self, movie_id: str, stars: int) -> Dict[str, Any]:
        item = {"id": str(uuid.uuid4()), "movieId": movie_id, "stars": stars}
        return self.ratings.create_item(body=item)

    def list_ratings(self, movie_id: str) -> List[Dict[str, Any]]:
        query = (
            "SELECT c.id, c.movieId, c.stars FROM c "
            "WHERE c.movieId = @movieId"
        )
        params: List[Dict[str, Any]] = [
            {"name": "@movieId", "value": movie_id}
        ]
        return list(
            self.ratings.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )

    def average_rating(self, movie_id: str) -> Optional[float]:
        ratings = self.list_ratings(movie_id)
        if not ratings:
            return None
        return round(sum(r["stars"] for r in ratings) / len(ratings), 2)

    # Comments
    def add_comment(self, movie_id: str, text: str) -> Dict[str, Any]:
        item = {"id": str(uuid.uuid4()), "movieId": movie_id, "text": text}
        return self.comments.create_item(body=item)

    def list_comments(self, movie_id: str) -> List[Dict[str, Any]]:
        query = (
            "SELECT c.id, c.movieId, c.text FROM c "
            "WHERE c.movieId = @movieId"
        )
        params: List[Dict[str, Any]] = [
            {"name": "@movieId", "value": movie_id}
        ]
        return list(
            self.comments.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )


@lru_cache(maxsize=1)
def get_cosmos() -> DB:
    use_mem = os.environ.get("USE_INMEMORY", "0").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if use_mem:
        return MemoryDB()  # type: ignore[return-value]
    return DB()


class MemoryDB:
    """Simple in-memory stand-in for Cosmos DB, for demos/offline mode.

    Enabled by setting USE_INMEMORY=1. Implements the same methods as DB.
    """

    def __init__(self) -> None:
        self._movies: Dict[str, Dict[str, Any]] = {}
        self._ratings: List[Dict[str, Any]] = []
        self._comments: List[Dict[str, Any]] = []

    # Movies
    def list_movies(self) -> List[Dict[str, Any]]:
        return list(self._movies.values())

    def create_movie(self, title: str) -> Dict[str, Any]:
        mid = str(uuid.uuid4())
        item = {"id": mid, "title": title}
        self._movies[mid] = item
        return item

    def get_movie(self, movie_id: str) -> Optional[Dict[str, Any]]:
        return self._movies.get(movie_id)

    # Ratings
    def add_rating(self, movie_id: str, stars: int) -> Dict[str, Any]:
        item = {"id": str(uuid.uuid4()), "movieId": movie_id, "stars": stars}
        self._ratings.append(item)
        return item

    def list_ratings(self, movie_id: str) -> List[Dict[str, Any]]:
        return [r for r in self._ratings if r.get("movieId") == movie_id]

    def average_rating(self, movie_id: str) -> Optional[float]:
        ratings = self.list_ratings(movie_id)
        if not ratings:
            return None
        return round(sum(r["stars"] for r in ratings) / len(ratings), 2)

    # Comments
    def add_comment(self, movie_id: str, text: str) -> Dict[str, Any]:
        item = {"id": str(uuid.uuid4()), "movieId": movie_id, "text": text}
        self._comments.append(item)
        return item

    def list_comments(self, movie_id: str) -> List[Dict[str, Any]]:
        return [c for c in self._comments if c.get("movieId") == movie_id]
