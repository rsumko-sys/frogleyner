import asyncio
import datetime as dt
import random

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from db import Database
from content.frog_texts import pick, RANDOM_THOUGHTS
from content.frog_facts_200 import FACTS_200 as FROG_FACTS
from content.frog_jokes_200 import JOKES_200 as FROG_JOKES

from content.leiner_quotes_ru import (
    PHILO,
    CHAOS,
    SLEEP,
    CARE,
    CHECK_2D,
    CHECK_3D,
    CHECK_5D,
    MICRO,
    ONE_WORD,
)

def frog_fact():
    return random.choice(FROG_FACTS)

def frog_joke():
    return random.choice(FROG_JOKES)


def _days_since(iso_ts: str) -> int:
    try:
        last = dt.datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except Exception:
        return 999
    now = dt.datetime.utcnow()
    return (now - last.replace(tzinfo=None)).days


def choose_mood(u) -> str:
    calm = 0.40
    philo = 0.25
    chaos = 0.20
    sleepy = 0.15

    fr = int(u.get("friendship_level") or 0)
    an = int(u.get("annoyance") or 0)
    care = int(u.get("care_mode") or 0)

    if fr >= 70:
        philo += 0.05
        calm += 0.05
    if an >= 60:
        chaos -= 0.05
        sleepy += 0.05
    if care == 1:
        calm += 0.10
        chaos -= 0.05

    weights = [
        ("calm", max(0.05, calm)),
        ("philo", max(0.05, philo)),
        ("chaos", max(0.05, chaos)),
        ("sleepy", max(0.05, sleepy)),
    ]
    total = sum(w for _, w in weights)
    r = random.random() * total
    c = 0.0
    for name, w in weights:
        c += w
        if r <= c:
            return name
    return "calm"


def should_speak(u) -> bool:
    p_speak = 0.60
    fr = int(u.get("friendship_level") or 0)
    an = int(u.get("annoyance") or 0)
    care = int(u.get("care_mode") or 0)

    if fr >= 60:
        p_speak += 0.10
    if an >= 60:
        p_speak -= 0.25
    if care == 1:
        p_speak += 0.10

    p_speak = min(0.85, max(0.20, p_speak))
    return random.random() < p_speak


def burst_len(u) -> int:
    fr = int(u.get("friendship_level") or 0)
    an = int(u.get("annoyance") or 0)
    if an >= 70:
        return 1
    p = 0.18 + (0.06 if fr >= 70 else 0.0)
    if random.random() < p:
        return random.choice([2, 3])
    return 1


def gen_line(u, mood: str) -> str:
    if random.random() < 0.05:
        return "..."
    if random.random() < 0.12:
        return random.choice(ONE_WORD)

    if int(u.get("care_mode") or 0) == 1:
        return random.choice(CARE)

    if mood == "sleepy":
        return random.choice(SLEEP)
    if mood == "philo":
        return random.choice(PHILO)
    if mood == "chaos":
        return random.choice(CHAOS)

    return random.choice(MICRO + [pick(RANDOM_THOUGHTS)])


async def safe_send(bot: Bot, db: Database, user_id: int, text: str):
    try:
        await bot.send_chat_action(user_id, "typing")
        await asyncio.sleep(random.uniform(1.0, 3.0))
        await bot.send_message(user_id, text)
    except TelegramForbiddenError:
        await db.set_autopush(user_id, False)
    except Exception:
        pass


async def friendship_tick(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        if not should_speak(u):
            continue
        mood = choose_mood(u)
        n = burst_len(u)
        for i in range(n):
            line = gen_line(u, mood)
            await safe_send(bot, db, u["user_id"], line)
            if i < n - 1:
                await asyncio.sleep(random.randint(5, 40))


async def silence_check(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        days = _days_since(u["last_seen"])

        if days >= 5:
            await db.set_care_mode(u["user_id"], True)
            msg = random.choice(CHECK_5D)
            await safe_send(bot, db, u["user_id"], msg)
        elif days == 3:
            await db.set_care_mode(u["user_id"], True)
            msg = random.choice(CHECK_3D)
            await safe_send(bot, db, u["user_id"], msg)
        elif days == 2:
            msg = random.choice(CHECK_2D)
            await safe_send(bot, db, u["user_id"], msg)
        elif days == 0 and int(u.get("care_mode") or 0) == 1:
            await db.set_care_mode(u["user_id"], False)
