import datetime as dt
import random
import logging

from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from db import Database
from content.frog_texts import pick, MORNING, WATER_PINGS, FOOD_PINGS, GYM_PINGS, SLEEP_PINGS, RANDOM_THOUGHTS
from frog_brain import friendship_tick, silence_check, safe_send

log = logging.getLogger("scheduler")


def _kb_water():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="Я выпил(а) 250 мл", callback_data="water:250")
    return kb.as_markup()


def _kb_yesno():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="gym:yes")
    kb.button(text="Нет", callback_data="gym:no")
    return kb.as_markup()


async def _safe_send(bot: Bot, db: Database, user_id: int, text: str, **kwargs):
    try:
        await bot.send_message(chat_id=user_id, text=text, **kwargs)
    except TelegramForbiddenError:
        await db.set_autopush(user_id, False)
        log.info("User %s blocked bot; autopush disabled", user_id)
    except TelegramBadRequest as e:
        log.warning("BadRequest to %s: %s", user_id, e)
    except Exception as e:
        log.exception("Send error to %s: %s", user_id, e)


async def broadcast_morning(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        await _safe_send(bot, db, u["user_id"], pick(MORNING))


async def broadcast_water(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        await _safe_send(bot, db, u["user_id"], pick(WATER_PINGS), reply_markup=_kb_water())


async def broadcast_food(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        await _safe_send(bot, db, u["user_id"], pick(FOOD_PINGS))


async def broadcast_random(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        if random.random() < 0.30:
            continue
        if random.random() < 0.5:
            ev = await db.random_event()
            text = ev["text"] if ev else pick(RANDOM_THOUGHTS)
        else:
            text = pick(RANDOM_THOUGHTS)
        await _safe_send(bot, db, u["user_id"], text)


async def broadcast_gym(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        await _safe_send(bot, db, u["user_id"], pick(GYM_PINGS), reply_markup=_kb_yesno())


async def broadcast_sleep(bot: Bot, db: Database):
    users = await db.get_autopush_users()
    for u in users:
        await _safe_send(bot, db, u["user_id"], pick(SLEEP_PINGS))


def next_interval() -> dt.datetime:
    minutes = random.randint(45, 120)
    return dt.datetime.now(timezone.utc) + dt.timedelta(minutes=minutes)


async def brain_job(bot: Bot, db: Database, scheduler: AsyncIOScheduler):
    await friendship_tick(bot, db)
    scheduler.add_job(
        brain_job,
        "date",
        run_date=next_interval(),
        args=[bot, db, scheduler],
        id="frog_brain",
        replace_existing=True,
    )


def build_scheduler(bot: Bot, db: Database) -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone="Europe/Kyiv")

    sched.add_job(
        lambda: broadcast_morning(bot, db),
        "cron",
        hour=7,
        minute=30,
        id="morning",
    )
    sched.add_job(
        lambda: broadcast_water(bot, db),
        "cron",
        hour=9,
        minute=0,
        id="water",
    )
    sched.add_job(
        lambda: broadcast_food(bot, db),
        "cron",
        hour=13,
        minute=0,
        id="food",
    )
    sched.add_job(
        lambda: broadcast_random(bot, db),
        "cron",
        hour=16,
        minute=0,
        id="random",
    )
    sched.add_job(
        lambda: broadcast_gym(bot, db),
        "cron",
        hour=19,
        minute=0,
        id="gym",
    )
    sched.add_job(
        lambda: broadcast_sleep(bot, db),
        "cron",
        hour=22,
        minute=30,
        id="sleep",
    )

    _first_run = dt.datetime.now(timezone.utc) + dt.timedelta(minutes=1)
    sched.add_job(
        brain_job,
        "date",
        run_date=_first_run,
        args=[bot, db, sched],
        id="frog_brain",
    )

    sched.add_job(
        lambda: silence_check(bot, db),
        "interval",
        hours=12,
        id="frog_silence",
    )

    return sched
