"""SQLite database management for Victoria Emergency feed data."""

import gzip
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import sqlite_utils
from rich.console import Console

console = Console()

DEFAULT_DB_PATH = "vicalerts.sqlite"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS feeds_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    etag TEXT,
    payload BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    feed_type TEXT NOT NULL,
    source_org TEXT,
    category1 TEXT,
    category2 TEXT
);

CREATE TABLE IF NOT EXISTS event_versions (
    event_id INTEGER NOT NULL,
    version_ts TEXT NOT NULL,
    status TEXT,
    headline TEXT,
    category TEXT,
    lat REAL,
    lon REAL,
    location TEXT,
    size_fmt TEXT,
    raw_props BLOB NOT NULL,
    PRIMARY KEY (event_id, version_ts),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE INDEX IF NOT EXISTS idx_event_versions_event_id ON event_versions(event_id);
CREATE INDEX IF NOT EXISTS idx_events_feed_type ON events(feed_type);
CREATE INDEX IF NOT EXISTS idx_events_last_seen ON events(last_seen);
"""


class Database:
    """Database wrapper for Victoria Emergency data."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db = sqlite_utils.Database(self.db_path)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        self.db.executescript(SCHEMA_SQL)

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        with self.db.conn:
            yield self.db

    def store_raw_feed(
        self, feed_data: dict[str, Any], etag: str | None = None, fetched_at: str = None
    ) -> int:
        """Store compressed raw feed data."""
        from datetime import datetime, timezone

        if not fetched_at:
            fetched_at = datetime.now(timezone.utc).isoformat()

        # Compress JSON payload
        json_bytes = json.dumps(feed_data, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(json_bytes)

        table = self.db["feeds_raw"]
        row_id = table.insert(
            {"fetched_at": fetched_at, "etag": etag, "payload": compressed}
        ).last_pk

        return row_id

    def get_latest_etag(self) -> str | None:
        """Get the ETag from the most recent successful fetch."""
        result = self.db.execute(
            "SELECT etag FROM feeds_raw WHERE etag IS NOT NULL ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else None

    def get_raw_feed(self, feed_id: int) -> dict[str, Any] | None:
        """Retrieve and decompress a raw feed by ID."""
        result = self.db.execute(
            "SELECT payload FROM feeds_raw WHERE id = ?", [feed_id]
        ).fetchone()

        if not result:
            return None

        compressed = result[0]
        json_bytes = gzip.decompress(compressed)
        return json.loads(json_bytes.decode("utf-8"))

    def upsert_event(
        self,
        event_id: int,
        feed_type: str,
        source_org: str,
        category1: str | None,
        category2: str | None,
        timestamp: str,
    ) -> None:
        """Insert or update an event record."""
        table = self.db["events"]

        # Check if event exists
        existing = table.rows_where("event_id = ?", [event_id])
        existing_list = list(existing)

        if existing_list:
            # Update last_seen
            table.update(event_id, {"last_seen": timestamp})
        else:
            # Insert new event
            table.insert(
                {
                    "event_id": event_id,
                    "first_seen": timestamp,
                    "last_seen": timestamp,
                    "feed_type": feed_type,
                    "source_org": source_org,
                    "category1": category1,
                    "category2": category2,
                }
            )

    def add_event_version(
        self,
        event_id: int,
        version_ts: str,
        status: str | None,
        headline: str | None,
        category: str | None,
        lat: float | None,
        lon: float | None,
        location: str | None,
        size_fmt: str | None,
        raw_props: dict[str, Any],
    ) -> bool:
        """Add a new event version if it doesn't exist."""
        table = self.db["event_versions"]

        # Check if this version already exists
        existing = self.db.execute(
            "SELECT 1 FROM event_versions WHERE event_id = ? AND version_ts = ?",
            [event_id, version_ts],
        ).fetchone()

        if existing:
            return False

        # Compress properties
        json_bytes = json.dumps(raw_props, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(json_bytes)

        table.insert(
            {
                "event_id": event_id,
                "version_ts": version_ts,
                "status": status,
                "headline": headline,
                "category": category,
                "lat": lat,
                "lon": lon,
                "location": location,
                "size_fmt": size_fmt,
                "raw_props": compressed,
            }
        )

        return True

    def get_event_versions(self, event_id: int) -> list[dict[str, Any]]:
        """Get all versions of an event."""
        results = []

        for row in self.db.execute(
            "SELECT * FROM event_versions WHERE event_id = ? ORDER BY version_ts",
            [event_id],
        ):
            # Decompress properties
            compressed = row[9]  # raw_props column
            json_bytes = gzip.decompress(compressed)
            raw_props = json.loads(json_bytes.decode("utf-8"))

            results.append(
                {
                    "event_id": row[0],
                    "version_ts": row[1],
                    "status": row[2],
                    "headline": row[3],
                    "category": row[4],
                    "lat": row[5],
                    "lon": row[6],
                    "location": row[7],
                    "size_fmt": row[8],
                    "raw_props": raw_props,
                }
            )

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        stats = {
            "total_feeds": self.db.execute("SELECT COUNT(*) FROM feeds_raw").fetchone()[
                0
            ],
            "total_events": self.db.execute("SELECT COUNT(*) FROM events").fetchone()[
                0
            ],
            "total_versions": self.db.execute(
                "SELECT COUNT(*) FROM event_versions"
            ).fetchone()[0],
        }

        # Get events by feed type
        feed_types = {}
        for row in self.db.execute(
            "SELECT feed_type, COUNT(*) FROM events GROUP BY feed_type"
        ):
            feed_types[row[0]] = row[1]
        stats["events_by_type"] = feed_types

        return stats
