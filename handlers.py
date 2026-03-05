import datetime as dt
import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Database
from content.frog_texts import pick, RANDOM_THOUGHTS
from content.leiner_quotes_ru import ONE_WORD
from content.markov import MarkovNgram
from personalize import display_name, personalize


def kb_water() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Я выпил(а) 250 мл", callback_data="water:250")
    return kb.as_markup()


def kb_yesno(kind: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data=f"{kind}:yes")
    kb.button(text="Нет", callback_data=f"{kind}:no")
    return kb.as_markup()


def kb_react(item_type: str, item_id: int | None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    base = f"react:{item_type}:{item_id if item_id is not None else 'none'}:"
    kb.button(text="👍 Ржач", callback_data=base + "like")
    kb.button(text="🤨 Таке", callback_data=base + "meh")
    kb.button(text="💀 Умер", callback_data=base + "dead")
    kb.adjust(3)
    return kb.as_markup()


def target_water_ml(weight_kg: float | None) -> int:
    if weight_kg and weight_kg > 0:
        return int(round(weight_kg * 35))
    return 2500


def frog_percent(water_today: int, target: int) -> int:
    if target <= 0:
        return 0
    return min(100, int(round(100 * (water_today / target))))


router = Router()


async def _user_ctx(m: Message, db: Database, host_user_id: int):
    """Обновляет имя в БД, возвращает (uid, name, is_host)."""
    uid = m.from_user.id if m.from_user else 0
    first = m.from_user.first_name if m.from_user else None
    if uid and first is not None:
        await db.update_user_name(uid, first)
    is_host = host_user_id and uid == host_user_id
    name = display_name(first, is_host)
    return uid, name, is_host


async def _name_for_user(uid: int, db: Database, host_user_id: int):
    """По user_id возвращает (name, is_host) из БД (для callback)."""
    u = await db.get_user(uid)
    try:
        first = u["first_name"] if u else None
    except (KeyError, TypeError):
        first = None
    is_host = host_user_id and uid == host_user_id
    return display_name(first, is_host), is_host


@router.message(Command("start"))
async def start(m: Message, db: Database, host_user_id: int = 0):
    uid, name, is_host = await _user_ctx(m, db, host_user_id)
    await db.upsert_user(uid, first_name=m.from_user.first_name if m.from_user else None)
    text = (
        "Ква. Я — Жаба Лейнера.\n"
        "Я сама буду писать тебе (если не замьютишь).\n\n"
        "Команды: /frog /frogday /water /drink /protein (кг) /mute /unmute /help"
    )
    await m.answer(personalize(text, name, is_host))


@router.message(Command("help"))
async def help_cmd(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    text = (
        "Ква.\n"
        "/frog — случайная реплика\n"
        "/frogday — жаба дня\n"
        "/water — вода сегодня + % жабности\n"
        "/drink — +250 мл\n"
        "/protein 80 — белок на день\n"
        "/setweight 80 — вес для воды\n"
        "/joke — марковская шутка\n"
        "/fact — факт про жаб, болото, воду\n"
        "/fortune — предсказание\n"
        "/mute /unmute — выключить/включить мои авто-пинги"
    )
    await m.answer(personalize(text, name, is_host))


@router.message(Command("menu"))
async def menu(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    text = (
        "🐸 Меню:\n\n"
        "/frog — реплика\n"
        "/frogday — жаба дня\n"
        "/water — вода\n"
        "/drink — +250 мл\n"
        "/joke — шутка\n"
        "/fact — факт про жаб і болото\n"
        "/fortune — предсказание\n"
        "/help — полная справка"
    )
    await m.answer(personalize(text, name, is_host))


@router.message(Command("status"))
async def status(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("Система работает.\nЖаба жива. Ква.", name, is_host))


@router.message(Command("ping"))
async def ping(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("pong 🐸", name, is_host))


FORTUNES = [
    "Болото принесёт удачу.",
    "Сегодня день хаоса. Ква.",
    "Жаба видит новые возможности.",
    "Всё пойдёт странно, но правильно.",
]


@router.message(Command("fortune"))
async def fortune(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("🔮 " + random.choice(FORTUNES), name, is_host))


@router.message(Command("secret"))
async def secret(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("🕳 Секрет болота активирован. Ква.", name, is_host))


@router.message(Command("mute"))
async def mute(m: Message, db: Database, host_user_id: int = 0):
    if m.from_user:
        await db.set_autopush(m.from_user.id, False)
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("Ок. Я замолкаю. Но я всё вижу. Ква.", name, is_host))


@router.message(Command("unmute"))
async def unmute(m: Message, db: Database, host_user_id: int = 0):
    if m.from_user:
        await db.set_autopush(m.from_user.id, True)
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("Ква. Я снова в эфире. Без фанатизма. Почти.", name, is_host))


@router.message(Command("setweight"))
async def setweight(m: Message, db: Database, host_user_id: int = 0):
    parts = (m.text or "").strip().split()
    if len(parts) < 2:
        await m.answer("Напиши так: /setweight 80")
        return
    try:
        w = float(parts[1].replace(",", "."))
        if w <= 0 or w > 400:
            raise ValueError()
    except ValueError:
        await m.answer("Вес выглядит подозрительно. Напиши число, типа 80.")
        return
    if m.from_user:
        await db.set_weight(m.from_user.id, w)
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize(f"Принято. Вес {w:g} кг. Теперь я считаю твою жабность точнее. Ква.", name, is_host))


FROG_MOOD = {
    "frog_rage": "Жаба в ярости. Ква.",
    "frog_party": "Жаба празднует. Ква.",
    "frog_detective": "Жаба что-то расследует. Пока безрезультатно. Ква.",
    "frog_think": "Жаба думает. Люди странные. Ква.",
    "frog_zen": "Жаба медитирует. Тишина. Ква.",
    "frog_attack": "Боевая жаба на связи. Ква.",
    "frog_lazy": "Ленивая жаба. Ничего не буду. Ква.",
    "frog_crazy": "Безумная жаба. Всё нормально. Ква.",
    "frog_sleep": "Жаба спит. Не буди. Ква.",
    "frog_mood": "Настроение жабы: ква. Ква.",
}


@router.message(Command("frog"))
async def frog(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    if m.from_user:
        await db.touch_user(m.from_user.id)
        await db.bump_friendship(m.from_user.id, 2)
    await m.answer(personalize(pick(RANDOM_THOUGHTS), name, is_host))


@router.message(Command("frog_rage", "frog_party", "frog_detective", "frog_think", "frog_zen", "frog_attack", "frog_lazy", "frog_crazy", "frog_sleep", "frog_mood"))
async def frog_mood_cmd(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    cmd = (m.text or "").strip().split()[0].lstrip("/").lower()
    text = FROG_MOOD.get(cmd) or pick(RANDOM_THOUGHTS)
    await m.answer(personalize(text, name, is_host))


@router.message(Command("frog_random"))
async def frog_random(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    if m.from_user:
        await db.touch_user(m.from_user.id)
    await m.answer(personalize("🎲 " + pick(RANDOM_THOUGHTS), name, is_host))


@router.message(Command("frog_generate"))
async def frog_generate(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("Жаба придумала новые состояния. Ква.", name, is_host))


@router.message(Command("states"))
async def states_cmd(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await m.answer(personalize("Список состояний — жми /frog и /frogday, там вся жаба. Ква.", name, is_host))


@router.message(Command("protein"))
async def protein(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    parts = (m.text or "").strip().split()
    if len(parts) < 2:
        await m.answer(personalize("Напиши так: /protein 80", name, is_host))
        return
    try:
        w = float(parts[1].replace(",", "."))
    except ValueError:
        await m.answer(personalize("Дай число, бро.", name, is_host))
        return
    p = int(round(w * 2))
    await m.answer(personalize(f"На день: примерно {p} г белка.\nКва. Белок сам себя не съест.", name, is_host))


@router.message(Command("drink"))
async def drink(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    if m.from_user:
        await db.add_water(m.from_user.id, 250)
        await db.touch_user(m.from_user.id)
    await m.answer(personalize("Плюс 250 мл. Ты становишься более жабой. Ква.", name, is_host))


@router.message(Command("water"))
async def water(m: Message, db: Database, host_user_id: int = 0):
    uid, name, is_host = await _user_ctx(m, db, host_user_id)
    u = await db.get_user(uid)
    if not u:
        await db.upsert_user(uid, first_name=m.from_user.first_name if m.from_user else None)
        u = await db.get_user(uid)
    today = await db.water_today_ml(uid, u["tz"] if u else "Europe/Kyiv")
    target = target_water_ml(float(u["weight_kg"]) if u and u["weight_kg"] is not None else None)
    pct = frog_percent(today, target)
    text = f"Сегодня воды: {today} мл.\nЦель: {target} мл.\nТы сегодня на {pct}% жаба. Ква."
    await m.answer(personalize(text, name, is_host), reply_markup=kb_water())


@router.message(Command("frogday"))
async def frogday(m: Message, db: Database, host_user_id: int = 0):
    uid, name, is_host = await _user_ctx(m, db, host_user_id)
    u = await db.get_user(uid)
    if not u:
        await db.upsert_user(uid, first_name=m.from_user.first_name if m.from_user else None)
        u = await db.get_user(uid)

    day = dt.datetime.utcnow().date().isoformat()
    frog_id = await db.pick_frog_for_day(uid, day)
    frog = await db.get_frog_by_id(frog_id)
    if not frog:
        await m.answer("Жаб пока нет. Запусти seed.")
        return

    text = (
        "Жаба дня:\n"
        f"{frog['name_ru']}\n"
        f"{(frog['latin'] or '').strip()}\n\n"
        f"Где живёт: {frog['habitat_ru'] or '—'}\n"
        f"Факт: {frog['fact_ru'] or '—'}\n\n"
        "Ква."
    )
    await m.answer(personalize(text, name, is_host), reply_markup=kb_react("frog", frog_id))


@router.message(Command("joke"))
async def joke(m: Message, db: Database, host_user_id: int = 0):
    uid, name, is_host = await _user_ctx(m, db, host_user_id)
    try:
        jokes_rows = await db.fetchall("SELECT text FROM jokes ORDER BY id DESC LIMIT 300")
        corpus = [j["text"] for j in jokes_rows if j and j["text"]]

        if not corpus:
            await m.answer(personalize("ква. жаба думала. жаба передумала.", name, is_host))
            return

        # Якщо жартів мало — просто віддати випадковий з БД (гарантовано працює)
        if len(corpus) < 5:
            row = await db.random_joke()
            row = await db.random_joke()
            text = (row["text"] if row and row["text"] else None) or "ква. жаба думала. жаба передумала."
            if uid:
                await db.bump_friendship(uid, 2)
            await m.answer(personalize(text, name, is_host))
            return

        mk = MarkovNgram()
        mk.train(corpus)
        line1 = mk.generate()
        if random.random() < 0.35:
            line2 = mk.generate(max_tokens=14)
            text = f"{line1}\n{line2}"
        else:
            text = line1
        if not (text and text.strip()):
            row = await db.random_joke()
            text = (row["text"] if row and row["text"] else None) or "ква. жаба думала. жаба передумала."
    except Exception:
        row = await db.random_joke()
        text = (row["text"] if row and row["text"] else None) or "ква. жаба думала. жаба передумала."
        if uid:
            await db.bump_friendship(uid, 2)
        await m.answer(personalize(text or "ква. жаба думала. жаба передумала.", name, is_host))
        return

    if uid:
        await db.bump_friendship(uid, 2)
    await m.answer(personalize(text or "ква. жаба думала. жаба передумала.", name, is_host))


@router.message(Command("fact"))
async def fact_cmd(m: Message, db: Database, host_user_id: int = 0):
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    row = await db.random_fact()
    if not row or not row["text"]:
        await m.answer(personalize("Ква. Фактов пока нет — запусти seed.", name, is_host))
        return
    await m.answer(personalize(f"🐸 {row['text']}", name, is_host))


@router.callback_query(F.data.startswith("water:"))
async def cb_water(c: CallbackQuery, db: Database, host_user_id: int = 0):
    if not c.data or not c.from_user:
        await c.answer()
        return
    ml = int(c.data.split(":")[1])
    uid = c.from_user.id
    if c.from_user.first_name is not None:
        await db.update_user_name(uid, c.from_user.first_name)
    name, is_host = await _name_for_user(uid, db, host_user_id)
    await db.add_water(uid, ml)
    await c.answer(personalize("Записала. Ква.", name, is_host))
    u = await db.get_user(uid)
    today = await db.water_today_ml(uid, u["tz"] if u else "Europe/Kyiv")
    target = target_water_ml(float(u["weight_kg"]) if u and u["weight_kg"] is not None else None)
    pct = frog_percent(today, target)
    if c.message:
        await c.message.answer(personalize(f"+{ml} мл.\nСегодня: {today} мл.\nТы на {pct}% жаба. Ква.", name, is_host))


@router.callback_query(F.data.startswith("gym:"))
async def cb_gym(c: CallbackQuery, db: Database, host_user_id: int = 0):
    if not c.data or not c.from_user:
        await c.answer()
        return
    ans = c.data.split(":")[1]
    uid = c.from_user.id
    if c.from_user.first_name is not None:
        await db.update_user_name(uid, c.from_user.first_name)
    name, is_host = await _name_for_user(uid, db, host_user_id)
    await db.add_training_log(uid, "gym", ans)
    await c.answer()
    if c.message:
        if ans == "yes":
            await c.message.answer(personalize("Красиво. Жаба уважает. Ква.", name, is_host))
        else:
            await c.message.answer(personalize("Ок. Сегодня качаем выживание. Ква.", name, is_host))


@router.callback_query(F.data.startswith("react:"))
async def cb_react(c: CallbackQuery, db: Database):
    if not c.data or not c.from_user:
        await c.answer()
        return
    parts = c.data.split(":")
    if len(parts) < 4:
        await c.answer()
        return
    _, item_type, item_id_raw, reaction = parts[0], parts[1], parts[2], parts[3]
    item_id = None if item_id_raw == "none" else int(item_id_raw)
    uid = c.from_user.id
    await db.add_reaction(uid, item_type, item_id, reaction)

    if reaction == "like":
        await db.bump_friendship(uid, 4)
        await db.bump_annoyance(uid, -2)
    elif reaction == "meh":
        await db.bump_friendship(uid, 1)
    elif reaction == "dead":
        await db.bump_friendship(uid, -1)
        await db.bump_annoyance(uid, 6)

    ack = {
        "like": "Поняла. Ржач засчитан. Ква.",
        "meh": "Ок. Таке таке. Ква.",
        "dead": "Я тоже умерла. Ква.",
    }.get(reaction, "Ква.")
    await c.answer(ack, show_alert=False)


@router.message(F.text)
async def any_text(m: Message, db: Database, host_user_id: int = 0):
    if not m.from_user or not m.text or m.text.startswith("/"):
        return
    _, name, is_host = await _user_ctx(m, db, host_user_id)
    await db.touch_user(m.from_user.id)
    await db.bump_friendship(m.from_user.id, 2)
    if random.random() < 0.75:
        return
    reply = random.choice(ONE_WORD)
    await m.answer(personalize(reply, name, is_host))
