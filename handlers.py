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


@router.message(Command("start"))
async def start(m: Message, db: Database):
    await db.upsert_user(m.from_user.id if m.from_user else 0)
    await m.answer(
        "Ква. Я — Жаба Лейнера.\n"
        "Я сама буду писать тебе (если не замьютишь).\n\n"
        "Команды: /frog /frogday /water /drink /protein (кг) /mute /unmute /help"
    )


@router.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer(
        "Ква.\n"
        "/frog — случайная реплика\n"
        "/frogday — жаба дня\n"
        "/water — вода сегодня + % жабности\n"
        "/drink — +250 мл\n"
        "/protein 80 — белок на день\n"
        "/setweight 80 — вес для воды\n"
        "/joke — марковская шутка\n"
        "/fortune — предсказание\n"
        "/mute /unmute — выключить/включить мои авто-пинги"
    )


@router.message(Command("menu"))
async def menu(m: Message):
    await m.answer(
        "🐸 Меню:\n\n"
        "/frog — реплика\n"
        "/frogday — жаба дня\n"
        "/water — вода\n"
        "/drink — +250 мл\n"
        "/joke — шутка\n"
        "/fortune — предсказание\n"
        "/help — полная справка"
    )


@router.message(Command("status"))
async def status(m: Message):
    await m.answer("Система работает.\nЖаба жива. Ква.")


@router.message(Command("ping"))
async def ping(m: Message):
    await m.answer("pong 🐸")


FORTUNES = [
    "Болото принесёт удачу.",
    "Сегодня день хаоса. Ква.",
    "Жаба видит новые возможности.",
    "Всё пойдёт странно, но правильно.",
]


@router.message(Command("fortune"))
async def fortune(m: Message):
    await m.answer("🔮 " + random.choice(FORTUNES))


@router.message(Command("secret"))
async def secret(m: Message):
    await m.answer("🕳 Секрет болота активирован. Ква.")


@router.message(Command("mute"))
async def mute(m: Message, db: Database):
    if m.from_user:
        await db.set_autopush(m.from_user.id, False)
    await m.answer("Ок. Я замолкаю. Но я всё вижу. Ква.")


@router.message(Command("unmute"))
async def unmute(m: Message, db: Database):
    if m.from_user:
        await db.set_autopush(m.from_user.id, True)
    await m.answer("Ква. Я снова в эфире. Без фанатизма. Почти.")


@router.message(Command("setweight"))
async def setweight(m: Message, db: Database):
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
    await m.answer(f"Принято. Вес {w:g} кг. Теперь я считаю твою жабность точнее. Ква.")


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
async def frog(m: Message, db: Database):
    if m.from_user:
        await db.touch_user(m.from_user.id)
        await db.bump_friendship(m.from_user.id, 2)
    await m.answer(pick(RANDOM_THOUGHTS))


@router.message(Command("frog_rage", "frog_party", "frog_detective", "frog_think", "frog_zen", "frog_attack", "frog_lazy", "frog_crazy", "frog_sleep", "frog_mood"))
async def frog_mood_cmd(m: Message):
    cmd = (m.text or "").strip().split()[0].lstrip("/").lower()
    text = FROG_MOOD.get(cmd) or pick(RANDOM_THOUGHTS)
    await m.answer(text)


@router.message(Command("frog_random"))
async def frog_random(m: Message, db: Database):
    if m.from_user:
        await db.touch_user(m.from_user.id)
    await m.answer("🎲 " + pick(RANDOM_THOUGHTS))


@router.message(Command("frog_generate"))
async def frog_generate(m: Message):
    await m.answer("Жаба придумала новые состояния. Ква.")


@router.message(Command("states"))
async def states_cmd(m: Message):
    await m.answer("Список состояний — жми /frog и /frogday, там вся жаба. Ква.")


@router.message(Command("protein"))
async def protein(m: Message):
    parts = (m.text or "").strip().split()
    if len(parts) < 2:
        await m.answer("Напиши так: /protein 80")
        return
    try:
        w = float(parts[1].replace(",", "."))
    except ValueError:
        await m.answer("Дай число, бро.")
        return
    p = int(round(w * 2))
    await m.answer(f"На день: примерно {p} г белка.\nКва. Белок сам себя не съест.")


@router.message(Command("drink"))
async def drink(m: Message, db: Database):
    if m.from_user:
        await db.add_water(m.from_user.id, 250)
        await db.touch_user(m.from_user.id)
    await m.answer("Плюс 250 мл. Ты становишься более жабой. Ква.")


@router.message(Command("water"))
async def water(m: Message, db: Database):
    uid = m.from_user.id if m.from_user else 0
    u = await db.get_user(uid)
    if not u:
        await db.upsert_user(uid)
        u = await db.get_user(uid)
    today = await db.water_today_ml(uid, u["tz"] if u else "Europe/Kyiv")
    target = target_water_ml(float(u["weight_kg"]) if u and u["weight_kg"] is not None else None)
    pct = frog_percent(today, target)
    await m.answer(
        f"Сегодня воды: {today} мл.\nЦель: {target} мл.\nТы сегодня на {pct}% жаба. Ква.",
        reply_markup=kb_water(),
    )


@router.message(Command("frogday"))
async def frogday(m: Message, db: Database):
    uid = m.from_user.id if m.from_user else 0
    u = await db.get_user(uid)
    if not u:
        await db.upsert_user(uid)
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
    await m.answer(text, reply_markup=kb_react("frog", frog_id))


@router.message(Command("joke"))
async def joke(m: Message, db: Database):
    uid = m.from_user.id if m.from_user else 0
    jokes_rows = await db.fetchall("SELECT text FROM jokes ORDER BY id DESC LIMIT 300")
    corpus = [j["text"] for j in jokes_rows if j and j.get("text")]

    if not corpus:
        await m.answer("ква. жаба думала. жаба передумала.")
        return

    mk = MarkovNgram()
    mk.train(corpus)
    line1 = mk.generate()
    if random.random() < 0.35:
        line2 = mk.generate(max_tokens=14)
        text = f"{line1}\n{line2}"
    else:
        text = line1

    if uid:
        await db.bump_friendship(uid, 2)
    await m.answer(text)


@router.callback_query(F.data.startswith("water:"))
async def cb_water(c: CallbackQuery, db: Database):
    if not c.data or not c.from_user:
        await c.answer()
        return
    ml = int(c.data.split(":")[1])
    uid = c.from_user.id
    await db.add_water(uid, ml)
    await c.answer("Записала. Ква.")
    u = await db.get_user(uid)
    today = await db.water_today_ml(uid, u["tz"] if u else "Europe/Kyiv")
    target = target_water_ml(float(u["weight_kg"]) if u and u["weight_kg"] is not None else None)
    pct = frog_percent(today, target)
    if c.message:
        await c.message.answer(f"+{ml} мл.\nСегодня: {today} мл.\nТы на {pct}% жаба.")


@router.callback_query(F.data.startswith("gym:"))
async def cb_gym(c: CallbackQuery, db: Database):
    if not c.data or not c.from_user:
        await c.answer()
        return
    ans = c.data.split(":")[1]
    uid = c.from_user.id
    await db.add_training_log(uid, "gym", ans)
    await c.answer()
    if c.message:
        if ans == "yes":
            await c.message.answer("Красиво. Жаба уважает. Ква.")
        else:
            await c.message.answer("Ок. Сегодня качаем выживание. Ква.")


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
async def any_text(m: Message, db: Database):
    if not m.from_user or not m.text or m.text.startswith("/"):
        return
    await db.touch_user(m.from_user.id)
    await db.bump_friendship(m.from_user.id, 2)
    if random.random() < 0.75:
        return
    reply = random.choice(ONE_WORD)
    await m.answer(reply)
