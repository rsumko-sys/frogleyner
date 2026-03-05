"""Smoke tests — перевірка що всі модулі бота імпортуються без помилок
незалежно від середовища (Docker, локально, CI)."""
import asyncio

import pytest


def test_content_frog_texts_imports():
    from content.frog_texts import pick, MORNING, WATER_PINGS, FOOD_PINGS
    from content.frog_texts import GYM_PINGS, SLEEP_PINGS, RANDOM_THOUGHTS

    assert callable(pick)
    for lst in (MORNING, WATER_PINGS, FOOD_PINGS, GYM_PINGS, SLEEP_PINGS, RANDOM_THOUGHTS):
        assert len(lst) > 0
        assert isinstance(pick(lst), str)


def test_content_leiner_quotes_imports():
    from content.leiner_quotes_ru import (
        PHILO, CHAOS, SLEEP, CARE,
        CHECK_2D, CHECK_3D, CHECK_5D,
        MICRO, ONE_WORD,
    )
    for lst in (PHILO, CHAOS, SLEEP, CARE, CHECK_2D, CHECK_3D, CHECK_5D, MICRO, ONE_WORD):
        assert len(lst) > 0


def test_markov_train_and_generate():
    from content.markov import MarkovNgram

    mk = MarkovNgram()
    corpus = [
        "жаба сидить у болоті і думає",
        "жаба пила воду і була щасливою",
        "жаба знає що болото це добре",
    ]
    mk.train(corpus)
    result = mk.generate()
    assert isinstance(result, str)
    assert len(result) > 0


def test_markov_empty_corpus():
    from content.markov import MarkovNgram

    mk = MarkovNgram()
    result = mk.generate()
    assert isinstance(result, str)


def test_db_schema_creates():
    import os
    import tempfile
    from db import Database

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        db = Database(path)
        asyncio.run(db.connect())
        asyncio.run(db.close())
    finally:
        os.unlink(path)


def test_seed_runs():
    import os
    import tempfile
    from seed import seed

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        asyncio.run(seed(path))
    finally:
        os.unlink(path)


def test_config_raises_without_token(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    from config import load_config

    with pytest.raises(RuntimeError, match="BOT_TOKEN"):
        load_config()


def test_config_loads_with_token(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test:token123")
    monkeypatch.setenv("DB_PATH", "leinerfrog.db")
    from config import load_config

    cfg = load_config()
    assert cfg.bot_token == "test:token123"
    assert cfg.db_path == "leinerfrog.db"


# ---------------------------------------------------------------------------
# handlers helpers
# ---------------------------------------------------------------------------

def test_handlers_target_water_ml():
    from handlers import target_water_ml

    assert target_water_ml(80) == 2800
    assert target_water_ml(60) == 2100
    assert target_water_ml(None) == 2500
    assert target_water_ml(0) == 2500      # non-positive → default


def test_handlers_frog_percent():
    from handlers import frog_percent

    assert frog_percent(1400, 2800) == 50
    assert frog_percent(2800, 2800) == 100
    assert frog_percent(3500, 2800) == 100  # capped at 100
    assert frog_percent(0, 2500) == 0
    assert frog_percent(100, 0) == 0        # zero target → 0, not crash


def test_handlers_keyboards_not_none():
    from handlers import kb_water, kb_yesno, kb_react

    assert kb_water() is not None
    assert kb_yesno("gym") is not None
    assert kb_react("frog", 7) is not None
    assert kb_react("frog", None) is not None


# ---------------------------------------------------------------------------
# frog_brain logic (pure functions, no network/bot)
# ---------------------------------------------------------------------------

def _fake_user(**kwargs):
    defaults = {"friendship_level": 50, "annoyance": 0, "care_mode": 0, "last_seen": "2026-01-01T00:00:00"}
    defaults.update(kwargs)
    return defaults


def test_frog_brain_choose_mood_returns_valid():
    from frog_brain import choose_mood

    u = _fake_user()
    valid = {"calm", "philo", "chaos", "sleepy"}
    for _ in range(50):
        assert choose_mood(u) in valid


def test_frog_brain_should_speak_respects_annoyance():
    from frog_brain import should_speak

    high_annoyance = _fake_user(annoyance=90)
    low_annoyance = _fake_user(annoyance=0, friendship_level=80)

    # fire each 200 times; high-annoyance user should speak much less often
    speaks_angry = sum(should_speak(high_annoyance) for _ in range(200))
    speaks_friendly = sum(should_speak(low_annoyance) for _ in range(200))
    assert speaks_friendly > speaks_angry


def test_frog_brain_gen_line_all_moods():
    from frog_brain import gen_line

    u = _fake_user()
    for mood in ("calm", "philo", "chaos", "sleepy"):
        line = gen_line(u, mood)
        assert isinstance(line, str) and len(line) > 0


def test_frog_brain_gen_line_care_mode():
    from frog_brain import gen_line
    from content.leiner_quotes_ru import CARE

    u = _fake_user(care_mode=1)
    # in care mode all generated lines must come from CARE
    lines = {gen_line(u, "calm") for _ in range(40)}
    # at least some should be CARE phrases (may rarely be ONE_WORD / "...")
    assert lines & set(CARE), "Expected at least one CARE line when care_mode=1"


def test_frog_brain_days_since():
    from frog_brain import _days_since
    import datetime as dt

    today = dt.datetime.now(dt.timezone.utc).isoformat()
    assert _days_since(today) == 0

    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=5)).isoformat()
    assert _days_since(old) == 5

    assert _days_since("not-a-date") == 999


def test_seed_populates_frogs_jokes_events():
    import os
    import tempfile
    from seed import seed, BUILTIN_FROGS, JOKES, EVENTS
    from db import Database

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        asyncio.run(seed(path))
        db = Database(path)

        async def check():
            await db.connect()
            n_frogs = await db.count_frogs()
            r_jokes = await db.fetchone("SELECT COUNT(1) AS c FROM jokes")
            r_events = await db.fetchone("SELECT COUNT(1) AS c FROM events")
            await db.close()
            return n_frogs, int(r_jokes["c"]), int(r_events["c"])

        n_frogs, n_jokes, n_events = asyncio.run(check())
        assert n_frogs == len(BUILTIN_FROGS)
        assert n_jokes == len(JOKES)
        assert n_events == len(EVENTS)
    finally:
        os.unlink(path)


def test_db_water_and_friendship_round_trip():
    import os
    import tempfile
    from db import Database

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        async def run():
            db = Database(path)
            await db.connect()
            await db.upsert_user(99)
            await db.add_water(99, 500)
            ml = await db.water_today_ml(99, "Europe/Kyiv")
            assert ml == 500, f"Expected 500 ml, got {ml}"
            await db.bump_friendship(99, 10)
            await db.bump_annoyance(99, 3)
            u = await db.get_user(99)
            assert int(u["friendship_level"]) == 10
            assert int(u["annoyance"]) == 3
            await db.close()

        asyncio.run(run())
    finally:
        os.unlink(path)
