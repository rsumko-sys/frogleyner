#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram бот "Жаба Лейнера" — виртуальный друг с характером.
Полноценный код для деплоя.
"""

import os
import logging
import sqlite3
import datetime
import random
import time
import json
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

# ======================== НАСТРОЙКИ ========================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======================== БАЗА ДАННЫХ (SQLite) ========================
DB_PATH = "frogbot.db"

def init_db():
    """Создание всех необходимых таблиц, если их нет."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Пользователи
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                frog_name TEXT DEFAULT 'Лягушонок',
                frog_color TEXT DEFAULT 'зелёный',
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Состояние лягушонка
        c.execute("""
            CREATE TABLE IF NOT EXISTS frog_state (
                user_id INTEGER PRIMARY KEY,
                hunger INTEGER DEFAULT 30,
                happiness INTEGER DEFAULT 50,
                energy INTEGER DEFAULT 70,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                last_fed TIMESTAMP,
                last_played TIMESTAMP,
                last_sleep TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        # Напоминания
        c.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                remind_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Настроения
        c.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                mood INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Достижения (простейшая таблица)
        c.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                user_id INTEGER,
                ach_code TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, ach_code)
            )
        """)
        conn.commit()

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return dict(row) if row else None

def create_user(user_id: int, username: str = "", first_name: str = ""):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name),
        )
        c.execute(
            "INSERT OR IGNORE INTO frog_state (user_id) VALUES (?)",
            (user_id,),
        )
        conn.commit()

def get_frog_state(user_id: int) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM frog_state WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return dict(row) if row else None

def update_frog_state(user_id: int, **kwargs):
    allowed = {"hunger", "happiness", "energy", "level", "exp", "last_fed", "last_played", "last_sleep"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(f"UPDATE frog_state SET {set_clause} WHERE user_id = ?", values)
        conn.commit()

def add_reminder(user_id: int, text: str, remind_time: datetime.datetime):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO reminders (user_id, text, remind_time) VALUES (?, ?, ?)",
            (user_id, text, remind_time),
        )
        conn.commit()
        return c.lastrowid

def delete_reminder(reminder_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()

def get_user_reminders(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM reminders WHERE user_id = ? AND remind_time > ? ORDER BY remind_time",
            (user_id, datetime.datetime.now()),
        )
        return [dict(row) for row in c.fetchall()]

def add_mood(user_id: int, mood: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO moods (user_id, mood) VALUES (?, ?)", (user_id, mood))
        conn.commit()

def add_achievement(user_id: int, ach_code: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO achievements (user_id, ach_code) VALUES (?, ?)",
                (user_id, ach_code),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_achievements(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT ach_code, unlocked_at FROM achievements WHERE user_id = ?", (user_id,))
        return [dict(row) for row in c.fetchall()]

# ======================== ПЛАНИРОВЩИК (APScheduler) ========================
scheduler = AsyncIOScheduler()

async def decrease_hunger_periodically():
    """Каждый час увеличиваем голод и немного уменьшаем счастье у всех лягушат."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT user_id, hunger, happiness FROM frog_state")
        frogs = c.fetchall()
        for frog in frogs:
            user_id = frog["user_id"]
            new_hunger = min(100, frog["hunger"] + 5)
            new_happiness = max(0, frog["happiness"] - (2 if new_hunger > 70 else 0))
            update_frog_state(user_id, hunger=new_hunger, happiness=new_happiness)

scheduler.add_job(decrease_hunger_periodically, IntervalTrigger(hours=1))

async def send_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str):
    """Отправляет напоминание пользователю."""
    await context.bot.send_message(chat_id=user_id, text=f"🔔 Напоминание: {text}")

# ======================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========================
def frogify(text: str) -> str:
    """Добавляет лягушачий колорит."""
    prefixes = ["🐸 ", "Ква-ква! ", "Риббит! ", "🐸 Слышал? ", ""]
    suffixes = [" 🐸", " Ква.", " Риббит.", " 🪰", ""]
    return random.choice(prefixes) + text + random.choice(suffixes)

def check_level_up(user_id: int):
    """Проверяет, не пора ли повысить уровень (на основе exp)."""
    state = get_frog_state(user_id)
    if not state:
        return False
    exp_needed = state["level"] * 100
    if state["exp"] >= exp_needed:
        new_level = state["level"] + 1
        update_frog_state(user_id, level=new_level, exp=state["exp"] - exp_needed)
        return True
    return False

# ======================== ОБРАБОТЧИКИ КОМАНД ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username or "", user.first_name or "")
    await update.message.reply_text(
        frogify(f"Привет, {user.first_name}! Я Жаба Лейнера — твой зелёный друг.\n"
                "Напиши /help, чтобы узнать, что я умею.")
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🐸 Вот что я могу:\n"
        "/adopt – завести лягушонка (если ещё нет)\n"
        "/feed – покормить\n"
        "/play – поиграть\n"
        "/status – состояние лягушонка\n"
        "/sleep – уложить спать\n"
        "/remind <текст> <ЧЧ:ММ> – напоминание\n"
        "/quote – мудрая цитата\n"
        "/game – мини-игры\n"
        "/weather <город> – погода (если есть API ключ)\n"
        "/mood <оценка 1-5> – записать настроение\n"
        "/profile – профиль и достижения\n"
        "А ещё я комментирую фото 😉"
    )
    await update.message.reply_text(frogify(text))

async def adopt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if user and user.get("frog_name") != "Лягушонок" or True:
        name = "Квася"
        if context.args:
            name = " ".join(context.args)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET frog_name = ? WHERE user_id = ?", (name, user_id))
            conn.commit()
        await update.message.reply_text(frogify(f"Отлично! Теперь твоего лягушонка зовут {name}."))
    else:
        await update.message.reply_text(frogify("У тебя уже есть лягушонок!"))

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_frog_state(user_id)
    if not state:
        await update.message.reply_text(frogify("Сначала заведи лягушонка командой /adopt"))
        return

    now = datetime.datetime.now()
    last_fed = state.get("last_fed")
    if last_fed:
        last_fed = datetime.datetime.fromisoformat(last_fed)
        if (now - last_fed).total_seconds() < 1800:
            await update.message.reply_text(frogify("Я ещё сыт! Подожди немного."))
            return

    new_hunger = max(0, state["hunger"] - 20)
    new_happiness = min(100, state["happiness"] + 10)
    new_exp = state["exp"] + 10
    update_frog_state(user_id, hunger=new_hunger, happiness=new_happiness, exp=new_exp, last_fed=now)

    if new_exp >= 100:
        add_achievement(user_id, "gourmet")

    if check_level_up(user_id):
        await update.message.reply_text(frogify("Спасибо за вкусняшку! 🐜\nУровень повышен!"))
    else:
        await update.message.reply_text(frogify("Спасибо за вкусняшку! 🐜"))

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_frog_state(user_id)
    if not state:
        await update.message.reply_text(frogify("Сначала заведи лягушонка командой /adopt"))
        return

    now = datetime.datetime.now()
    last_played = state.get("last_played")
    if last_played:
        last_played = datetime.datetime.fromisoformat(last_played)
        if (now - last_played).total_seconds() < 1800:
            await update.message.reply_text(frogify("Мы уже играли! Лягушонок устал."))
            return

    keyboard = [[InlineKeyboardButton("🐜 Ловит��!", callback_data="catch_fly")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Муха появилась! Лови быстрее!", reply_markup=reply_markup)
    context.user_data["fly_appeared"] = time.time()
    context.user_data["fly_user"] = user_id

async def catch_fly_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if context.user_data.get("fly_user") != user_id:
        await query.edit_message_text("Эта муха не для тебя!")
        return
    appeared = context.user_data.get("fly_appeared")
    if appeared and (time.time() - appeared) < 3:
        new_happiness = min(100, get_frog_state(user_id)["happiness"] + 15)
        new_exp = get_frog_state(user_id)["exp"] + 15
        update_frog_state(user_id, happiness=new_happiness, exp=new_exp, last_played=datetime.datetime.now())
        if check_level_up(user_id):
            await query.edit_message_text(frogify("🎉 Ты поймал муху! Уровень повышен!"))
        else:
            await query.edit_message_text(frogify("🎉 Ты поймал муху! +15 к счастью."))
        add_achievement(user_id, "fly_catcher")
    else:
        await query.edit_message_text(frogify("😢 Муха улетела... Попробуй ещё."))
    context.user_data.pop("fly_appeared", None)
    context.user_data.pop("fly_user", None)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_frog_state(user_id)
    if not state:
        await update.message.reply_text(frogify("Сначала заведи лягушонка командой /adopt"))
        return
    user = get_user(user_id)
    frog_name = user["frog_name"] if user else "Лягушонок"
    text = (
        f"🐸 {frog_name}:\n"
        f"🍽 Голод: {state['hunger']}/100\n"
        f"😊 Счастье: {state['happiness']}/100\n"
        f"⚡ Энергия: {state['energy']}/100\n"
        f"📊 Уровень: {state['level']} (опыт: {state['exp']}/{state['level']*100})"
    )
    await update.message.reply_text(frogify(text))

async def sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_frog_state(user_id)
    if not state:
        await update.message.reply_text(frogify("Сначала заведи лягушонка командой /adopt"))
        return
    now = datetime.datetime.now()
    last_sleep = state.get("last_sleep")
    if last_sleep:
        last_sleep = datetime.datetime.fromisoformat(last_sleep)
        if (now - last_sleep).total_seconds() < 7200:
            await update.message.reply_text(frogify("Я ещё не устал!"))
            return
    new_energy = min(100, state["energy"] + 30)
    update_frog_state(user_id, energy=new_energy, last_sleep=now)
    await update.message.reply_text(frogify("Хр-р-р... *храпит*"))

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Формат: /remind Купить молоко 18:30"""
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Формат: /remind <текст> <ЧЧ:ММ>")
            return
        time_str = args[-1]
        text = " ".join(args[:-1])
        remind_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        now = datetime.datetime.now()
        remind_datetime = datetime.datetime.combine(now.date(), remind_time)
        if remind_datetime < now:
            remind_datetime += datetime.timedelta(days=1)

        reminder_id = add_reminder(update.effective_user.id, text, remind_datetime)

        scheduler.add_job(
            send_reminder,
            trigger=DateTrigger(run_date=remind_datetime),
            args=[context.application, update.effective_user.id, text],
            id=f"remind_{reminder_id}",
            replace_existing=True,
        )

        await update.message.reply_text(
            frogify(f"Напомню тебе в {time_str}: {text}")
        )
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка в формате времени. Используй ЧЧ:ММ")

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Каждый день — новая возможность стать чуточку лучше.",
        "Даже с��мая маленькая лягушка может допрыгнуть до большой цели.",
        "Не бойся квакать громко — твой голос важен.",
        "Счастье — это когда мухи сами летят в рот.",
        "Главное — не забывать отдыхать на листе кувшинки.",
    ]
    await update.message.reply_text(frogify(random.choice(quotes)))

async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Поймай муху", callback_data="game_catch")],
        [InlineKeyboardButton("Лягушачьи бега (скоро)", callback_data="game_racing")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери игру:", reply_markup=reply_markup)

async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "game_catch":
        user_id = query.from_user.id
        keyboard = [[InlineKeyboardButton("🐜 Ловить!", callback_data="catch_fly")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Муха появилась! Лови быстрее!", reply_markup=reply_markup)
        context.user_data["fly_appeared"] = time.time()
        context.user_data["fly_user"] = user_id
    else:
        await query.edit_message_text("Эта игра ещё в разработке. Ква!")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not WEATHER_API_KEY:
        await update.message.reply_text(frogify("Погода временно недоступна (нет API ключа)."))
        return
    if not context.args:
        await update.message.reply_text("Укажи город: /weather Москва")
        return
    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        resp = requests.get(url)
        data = resp.json()
        if data.get("cod") != 200:
            await update.message.reply_text(frogify("Город не найден."))
            return
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        reply = f"Погода в {city}: {desc}, температура {temp}°C."
        if "дождь" in desc:
            reply += " Самое время для лягушки!"
        elif temp > 25:
            reply += " Жарковато, надо искупаться."
        elif temp < 5:
            reply += " Холодно, лучше спать."
        await update.message.reply_text(frogify(reply))
    except Exception as e:
        logger.error(e)
        await update.message.reply_text(frogify("Не удалось получить погоду."))

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи своё настроение от 1 до 5: /mood 4")
        return
    try:
        mood_val = int(context.args[0])
        if mood_val < 1 or mood_val > 5:
            raise ValueError
        add_mood(update.effective_user.id, mood_val)
        responses = {
            1: "Ой, всё так плохо? Хочешь поговорить?",
            2: "Грустно... Может, поиграем?",
            3: "Нормально, но могло быть лучше.",
            4: "Хорошо! Рад за тебя.",
            5: "Супер! Делись позитивом!",
        }
        await update.message.reply_text(frogify(responses[mood_val]))
    except ValueError:
        await update.message.reply_text("Настроение должно быть числом от 1 до 5.")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text(frogify("Сначала заведи лягушонка /adopt"))
        return
    state = get_frog_state(user_id)
    achievements = get_achievements(user_id)
    ach_names = {
        "gourmet": "Гурман (накормил 10 раз)",
        "fly_catcher": "Ловец мух (поймал муху в игре)",
    }
    ach_list = "\n".join([f"✅ {ach_names.get(a['ach_code'], a['ach_code'])}" for a in achievements])
    if not ach_list:
        ach_list = "Пока нет достижений."

    text = (
        f"👤 Профиль {update.effective_user.first_name}\n"
        f"🐸 Имя лягушонка: {user['frog_name']}\n"
        f"🎨 Цвет: {user['frog_color']}\n"
        f"📊 Уровень: {state['level']}\n\n"
        f"🏆 Достижения:\n{ach_list}"
    )
    await update.message.reply_text(frogify(text))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comments = [
        "О, красивое фото! Прямо как моя любимая кувшинка.",
        "Можно съесть?.. Ой, то есть, вкусный кадр!",
        "А на этом фото есть мухи?",
        "Ква-красота!",
    ]
    await update.message.reply_text(frogify(random.choice(comments)))

# ======================== ОСНОВНАЯ ФУНКЦИЯ ========================
def main():
    init_db()
    scheduler.start()

    app = Application.builder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("adopt", adopt))
    app.add_handler(CommandHandler("feed", feed))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("sleep", sleep))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("game", game_menu))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("profile", profile))

    # Callback'и для инлайн-кнопок
    app.add_handler(CallbackQueryHandler(catch_fly_callback, pattern="^catch_fly$"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^game_"))

    # Обработка фото
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
