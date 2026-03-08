import sqlite3
from contextlib import closing
from typing import List


class Stats:
    """Holds statistics of measurements"""

    tvoc_max: sqlite3.Row | None
    tvoc_min: sqlite3.Row | None
    co2_min: sqlite3.Row | None
    co2_max: sqlite3.Row | None


class DB:
    """Class for handling database interactions"""

    # sql
    CREATE_SQL = """
CREATE TABLE IF NOT EXISTS measurements
    (
        timestamp integer not null primary key,
        tvoc real not null,
        co2 real not null
    );
"""

    def __init__(self, db_name: str = "greetings.db"):
        """Class init"""
        self.db_name = db_name
        self._conn = sqlite3.connect(
            self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()
        cursor.execute(self.CREATE_SQL)
        self._conn.commit()

    def store(self, timestamp: int, tvoc: float, co2: float) -> int | None:
        """Adds a measurement"""
        with closing(self._conn.cursor()) as cursor:
            cursor.execute(
                # sql
                "INSERT INTO measurements (timestamp, tvoc, co2) VALUES (?, ?, ?)",
                (timestamp, tvoc, co2),
            )
            self._conn.commit()
            return cursor.lastrowid

    def get_stats(self) -> Stats:
        """Returns measurement statistics"""
        with closing(self._conn.cursor()) as cursor:
            # this could probably be made into a single query, but the database being sqlite results in much lower latency with multiple selects
            # returned object could also be better typed
            stats = Stats()
            cursor.execute(
                # sql
                "SELECT tvoc, timestamp FROM measurements ORDER BY tvoc DESC LIMIT 1"
            )
            stats.tvoc_max = cursor.fetchone()
            cursor.execute(
                # sql
                "SELECT tvoc, timestamp FROM measurements ORDER BY tvoc ASC LIMIT 1"
            )
            stats.tvoc_min = cursor.fetchone()
            cursor.execute(
                # sql
                "SELECT co2, timestamp FROM measurements ORDER BY co2 DESC LIMIT 1"
            )
            stats.co2_max = cursor.fetchone()
            cursor.execute(
                # sql
                "SELECT co2, timestamp FROM measurements ORDER BY co2 ASC LIMIT 1"
            )
            stats.co2_min = cursor.fetchone()
            return stats

    def get_page(self, page: int, page_size: int = 20) -> List[sqlite3.Row]:
        """Gets a paged list of all measurements. Page is 0 indexed."""
        with closing(self._conn.cursor()) as cur:
            cur = self._conn.cursor()
            cur.execute(
                # sql
                "SELECT timestamp, tvoc, co2 FROM measurements ORDER BY timestamp DESC LIMIT ?, ?",
                (page_size, page * page_size),
            )
            return cur.fetchall()

    def close(self) -> None:
        """Closes the DB connection"""
        self._conn.close()
