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
