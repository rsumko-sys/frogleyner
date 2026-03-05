import aiosqlite
import datetime as dt
from typing import Optional, Sequence, Any

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  tz TEXT NOT NULL DEFAULT 'Europe/Kyiv',
  autopush INTEGER NOT NULL DEFAULT 1,
  weight_kg REAL,
  friendship_level INTEGER NOT NULL DEFAULT 0,
  annoyance INTEGER NOT NULL DEFAULT 0,
  care_mode INTEGER NOT NULL DEFAULT 0,
  first_name TEXT,
  created_at TEXT NOT NULL,
  last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS water_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  ml INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS training_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  kind TEXT NOT NULL,
  note TEXT,
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS frog_species (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name_ru TEXT NOT NULL,
  latin TEXT,
  habitat_ru TEXT,
  fact_ru TEXT,
  image_url TEXT,
  tags TEXT
);

CREATE TABLE IF NOT EXISTS frog_day (
  user_id INTEGER NOT NULL,
  day_ymd TEXT NOT NULL,
  species_id INTEGER NOT NULL,
  PRIMARY KEY(user_id, day_ymd),
  FOREIGN KEY(user_id) REFERENCES users(user_id),
  FOREIGN KEY(species_id) REFERENCES frog_species(id)
);

CREATE TABLE IF NOT EXISTS jokes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  tags TEXT
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  tags TEXT
);

CREATE TABLE IF NOT EXISTS facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  tags TEXT
);

CREATE TABLE IF NOT EXISTS reactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  item_type TEXT NOT NULL,
  item_id INTEGER,
  reaction TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        self._db: Optional[aiosqlite.Connection] = None

    async def connect(self):
        self._db = await aiosqlite.connect(self.path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA_SQL)
        await self._db.commit()
        # Міграція: first_name для існуючих БД
        try:
            await self.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
        except Exception:
            pass

    async def close(self):
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def db(self) -> aiosqlite.Connection:
        assert self._db is not None
        return self._db

    async def execute(self, sql: str, params: Sequence[Any] = ()):
        await self.db.execute(sql, params)
        await self.db.commit()

    async def fetchone(self, sql: str, params: Sequence[Any] = ()):
        cur = await self.db.execute(sql, params)
        row = await cur.fetchone()
        await cur.close()
        return row

    async def fetchall(self, sql: str, params: Sequence[Any] = ()):
        cur = await self.db.execute(sql, params)
        rows = await cur.fetchall()
        await cur.close()
        return rows

    # --- Users ---
    async def upsert_user(self, user_id: int, tz: str = "Europe/Kyiv", first_name: str | None = None):
        now = dt.datetime.utcnow().isoformat()
        name = (first_name or "").strip() or None
        await self.execute(
            """
            INSERT INTO users(user_id, tz, autopush, first_name, created_at, last_seen)
            VALUES(?, ?, 1, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              tz=excluded.tz,
              last_seen=excluded.last_seen,
              first_name=COALESCE(excluded.first_name, first_name)
            """,
            (user_id, tz, name, now, now),
        )

    async def update_user_name(self, user_id: int, first_name: str | None):
        """Оновлює first_name при кожному зверненні (для персоналізації)."""
        name = (first_name or "").strip() or None
        await self.execute("UPDATE users SET first_name=? WHERE user_id=?", (name, user_id))

    async def touch_user(self, user_id: int):
        now = dt.datetime.utcnow().isoformat()
        await self.execute("UPDATE users SET last_seen=? WHERE user_id=?", (now, user_id))

    async def set_autopush(self, user_id: int, enabled: bool):
        await self.execute("UPDATE users SET autopush=? WHERE user_id=?", (1 if enabled else 0, user_id))

    async def set_weight(self, user_id: int, weight_kg: float):
        await self.execute("UPDATE users SET weight_kg=? WHERE user_id=?", (weight_kg, user_id))

    async def get_user(self, user_id: int):
        return await self.fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))

    async def get_autopush_users(self):
        return await self.fetchall("SELECT * FROM users WHERE autopush=1")

    async def bump_friendship(self, user_id: int, delta: int):
        await self.execute(
            "UPDATE users SET friendship_level = MAX(0, MIN(100, COALESCE(friendship_level,0) + ?)) WHERE user_id=?",
            (delta, user_id),
        )

    async def bump_annoyance(self, user_id: int, delta: int):
        await self.execute(
            "UPDATE users SET annoyance = MAX(0, MIN(100, COALESCE(annoyance,0) + ?)) WHERE user_id=?",
            (delta, user_id),
        )

    async def set_care_mode(self, user_id: int, enabled: bool):
        await self.execute("UPDATE users SET care_mode=? WHERE user_id=?", (1 if enabled else 0, user_id))

    # --- Water ---
    async def add_water(self, user_id: int, ml: int):
        now = dt.datetime.utcnow().isoformat()
        await self.execute(
            "INSERT INTO water_log(user_id, ts, ml) VALUES(?, ?, ?)",
            (user_id, now, ml),
        )

    async def water_today_ml(self, user_id: int, tz: str) -> int:
        today = dt.datetime.utcnow().date().isoformat()
        row = await self.fetchone(
            "SELECT COALESCE(SUM(ml),0) AS s FROM water_log WHERE user_id=? AND substr(ts,1,10)=?",
            (user_id, today),
        )
        return int(row["s"]) if row else 0

    # --- Frogs ---
    async def count_frogs(self) -> int:
        row = await self.fetchone("SELECT COUNT(1) AS c FROM frog_species")
        return int(row["c"]) if row else 0

    async def get_frog_by_id(self, frog_id: int):
        return await self.fetchone("SELECT * FROM frog_species WHERE id=?", (frog_id,))

    async def pick_frog_for_day(self, user_id: int, day_ymd: str) -> int:
        existing = await self.fetchone(
            "SELECT species_id FROM frog_day WHERE user_id=? AND day_ymd=?", (user_id, day_ymd)
        )
        if existing:
            return int(existing["species_id"])

        c = await self.count_frogs()
        if c <= 0:
            raise RuntimeError("frog_species is empty. Run seed.")
        seed = abs(hash(f"{user_id}:{day_ymd}"))
        offset = seed % c
        row = await self.fetchone("SELECT id FROM frog_species ORDER BY id LIMIT 1 OFFSET ?", (offset,))
        frog_id = int(row["id"])
        await self.execute(
            "INSERT INTO frog_day(user_id, day_ymd, species_id) VALUES(?,?,?)",
            (user_id, day_ymd, frog_id),
        )
        return frog_id

    # --- Content ---
    async def random_event(self):
        return await self.fetchone("SELECT * FROM events ORDER BY RANDOM() LIMIT 1")

    async def random_joke(self):
        return await self.fetchone("SELECT * FROM jokes ORDER BY RANDOM() LIMIT 1")

    async def random_fact(self):
        return await self.fetchone("SELECT * FROM facts ORDER BY RANDOM() LIMIT 1")

    async def add_reaction(self, user_id: int, item_type: str, item_id: Optional[int], reaction: str):
        now = dt.datetime.utcnow().isoformat()
        await self.execute(
            "INSERT INTO reactions(user_id, ts, item_type, item_id, reaction) VALUES(?,?,?,?,?)",
            (user_id, now, item_type, item_id, reaction),
        )

    async def add_training_log(self, user_id: int, kind: str, note: Optional[str] = None):
        now = dt.datetime.utcnow().isoformat()
        await self.execute(
            "INSERT INTO training_log(user_id, ts, kind, note) VALUES(?,?,?,?)",
            (user_id, now, kind, note),
        )
