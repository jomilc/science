from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Mapping

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    organization TEXT,
    url TEXT NOT NULL,
    snippet TEXT,
    source TEXT,
    category TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'new',
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    return connection


def upsert_jobs(connection: sqlite3.Connection, jobs: Iterable[Mapping[str, object]]) -> int:
    inserted = 0
    for job in jobs:
        cursor = connection.execute(
            """
            INSERT INTO jobs (
                fingerprint, title, organization, url, snippet, source,
                category, score, first_seen, last_seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(fingerprint) DO UPDATE SET
                title=excluded.title,
                organization=excluded.organization,
                snippet=excluded.snippet,
                source=excluded.source,
                category=excluded.category,
                score=MAX(jobs.score, excluded.score),
                last_seen=excluded.last_seen
            """,
            (
                job['fingerprint'], job['title'], job.get('organization'),
                job['url'], job.get('snippet'), job.get('source'),
                job.get('category'), job.get('score', 0),
                job['first_seen'], job['last_seen'],
            ),
        )
        inserted += int(cursor.rowcount == 1)
    connection.commit()
    return inserted
