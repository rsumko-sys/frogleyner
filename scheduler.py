import datetime as dt
import random
import logging

from datetime import timezone

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from db import Database
from content.frog_texts import (
    pick,
    MORNING,
    WATER_PINGS,
    FOOD_PINGS,
    GYM_PINGS,
    SLEEP_PINGS,
    RANDOM_THOUGHTS,
    CANCEL_AUTOPUSH_730,
    WEATHER_COMMENTS,
)
from frog_brain import friendship_tick, silence_check, safe_send
from personalize import display_name, personalize

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


async def broadcast_morning(bot: Bot, db: Database, host_user_id: int = 0):
    users = await db.get_autopush_users()
    base = pick(MORNING)
    for u in users:
        uid = u["user_id"]
        name = display_name(u.get("first_name"), host_user_id and uid == host_user_id)
        await _safe_send(bot, db, uid, personalize(base, name, host_user_id and uid == host_user_id))


async def _fetch_weather(api_key: str, city: str) -> tuple[float | None, str]:
    """Возвращает (temp_c, description) или (None, '') при ошибке."""
    if not api_key or not city:
        return None, ""
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric&lang=ru"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None, ""
                data = await resp.json()
                temp = data.get("main", {}).get("temp")
                weather = data.get("weather", [{}])
                desc = weather[0].get("description", "") if weather else ""
                return (float(temp), desc) if temp is not None else (None, desc)
    except Exception as e:
        log.warning("Weather fetch failed: %s", e)
        return None, ""


async def broadcast_cancel_autopush(bot: Bot, db: Database, host_user_id: int = 0):
    """7:30 — сообщение об отмене авто-рассылки до 8:00."""
    users = await db.get_autopush_users()
    base = pick(CANCEL_AUTOPUSH_730)
    for u in users:
        uid = u["user_id"]
        first = u.get("first_name")
        is_host = host_user_id and uid == host_user_id
        name = display_name(first, is_host)
        await _safe_send(bot, db, uid, personalize(base, name, is_host))


async def broadcast_weather(bot: Bot, db: Database, api_key: str, city: str, host_user_id: int = 0):
    """8:00 — прогноз погоды с ёбаным комментарием (по-русски)."""
    users = await db.get_autopush_users()
    temp, desc = await _fetch_weather(api_key, city)
    comment = pick(WEATHER_COMMENTS)
    if temp is not None and desc:
        line = f"🌡 {temp:+.0f}°C, {desc}"
        base = f"{comment}\n\n{line}\n\nКва."
    else:
        base = f"{comment}\n\nПогоду взять не удалось. Глянь в окно. Ква."
    for u in users:
        uid = u["user_id"]
        first = u.get("first_name")
        is_host = host_user_id and uid == host_user_id
        name = display_name(first, is_host)
        await _safe_send(bot, db, uid, personalize(base, name, is_host))


async def broadcast_water(bot: Bot, db: Database, host_user_id: int = 0):
    users = await db.get_autopush_users()
    base = pick(WATER_PINGS)
    for u in users:
        uid = u["user_id"]
        name = display_name(u.get("first_name"), host_user_id and uid == host_user_id)
        await _safe_send(bot, db, uid, personalize(base, name, host_user_id and uid == host_user_id), reply_markup=_kb_water())


async def broadcast_food(bot: Bot, db: Database, host_user_id: int = 0):
    users = await db.get_autopush_users()
    base = pick(FOOD_PINGS)
    for u in users:
        uid = u["user_id"]
        name = display_name(u.get("first_name"), host_user_id and uid == host_user_id)
        await _safe_send(bot, db, uid, personalize(base, name, host_user_id and uid == host_user_id))


async def broadcast_random(bot: Bot, db: Database, host_user_id: int = 0):
    users = await db.get_autopush_users()
    for u in users:
        if random.random() < 0.30:
            continue
        if random.random() < 0.5:
            ev = await db.random_event()
            base = ev["text"] if ev else pick(RANDOM_THOUGHTS)
        else:
            base = pick(RANDOM_THOUGHTS)
        uid = u["user_id"]
        name = display_name(u.get("first_name"), host_user_id and uid == host_user_id)
        await _safe_send(bot, db, uid, personalize(base, name, host_user_id and uid == host_user_id))


async def broadcast_gym(bot: Bot, db: Database, host_user_id: int = 0):
    users = await db.get_autopush_users()
    base = pick(GYM_PINGS)
    for u in users:
        uid = u["user_id"]
        name = display_name(u.get("first_name"), host_user_id and uid == host_user_id)
        await _safe_send(bot, db, uid, personalize(base, name, host_user_id and uid == host_user_id), reply_markup=_kb_yesno())


async def broadcast_sleep(bot: Bot, db: Database, host_user_id: int = 0):
    users = await db.get_autopush_users()
    base = pick(SLEEP_PINGS)
    for u in users:
        uid = u["user_id"]
        name = display_name(u.get("first_name"), host_user_id and uid == host_user_id)
        await _safe_send(bot, db, uid, personalize(base, name, host_user_id and uid == host_user_id))


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


def build_scheduler(
    bot: Bot,
    db: Database,
    openweather_api_key: str = "",
    weather_city: str = "Kyiv",
    host_user_id: int = 0,
) -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone="Europe/Kyiv")

    # 7:30 — отмена автоповідомлень (російською)
    sched.add_job(
        lambda: broadcast_cancel_autopush(bot, db, host_user_id),
        "cron",
        hour=7,
        minute=30,
        id="cancel_autopush",
    )
    # 8:00 — прогноз погоди з єбанутим коментарем (російською)
    sched.add_job(
        lambda: broadcast_weather(bot, db, openweather_api_key, weather_city, host_user_id),
        "cron",
        hour=8,
        minute=0,
        id="weather",
    )
    sched.add_job(
        lambda: broadcast_water(bot, db, host_user_id),
        "cron",
        hour=9,
        minute=0,
        id="water",
    )
    sched.add_job(
        lambda: broadcast_food(bot, db, host_user_id),
        "cron",
        hour=13,
        minute=0,
        id="food",
    )
    sched.add_job(
        lambda: broadcast_random(bot, db, host_user_id),
        "cron",
        hour=16,
        minute=0,
        id="random",
    )
    sched.add_job(
        lambda: broadcast_gym(bot, db, host_user_id),
        "cron",
        hour=19,
        minute=0,
        id="gym",
    )
    sched.add_job(
        lambda: broadcast_sleep(bot, db, host_user_id),
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
