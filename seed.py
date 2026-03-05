import asyncio
import json
import os
from pathlib import Path

from db import Database

DEFAULT_JSON = "frog_species_200.json"

# Вбудований мінімум жаб, якщо JSON немає
BUILTIN_FROGS = [
    {"name_ru": "Квакша обыкновенная", "latin": "Hyla arborea", "habitat_ru": "Европа, леса возле водоёмов", "fact_ru": "Может лазить по стеклу благодаря липким подушечкам", "image_url": "", "tags": "tree"},
    {"name_ru": "Стеклянная лягушка", "latin": "Centrolenidae", "habitat_ru": "Центральная и Южная Америка", "fact_ru": "У неё прозрачное брюхо — можно увидеть сердце", "image_url": "", "tags": "transparent"},
    {"name_ru": "Лягушка-бык", "latin": "Lithobates catesbeianus", "habitat_ru": "Северная Америка", "fact_ru": "Ест всё что помещается в рот, включая других лягушек", "image_url": "", "tags": "big"},
    {"name_ru": "Лягушка Голиаф", "latin": "Conraua goliath", "habitat_ru": "Камерун", "fact_ru": "Самая большая лягушка в мире", "image_url": "", "tags": "giant"},
    {"name_ru": "Золотая древолазка", "latin": "Phyllobates terribilis", "habitat_ru": "Колумбия", "fact_ru": "Одна из самых ядовитых лягушек на планете", "image_url": "", "tags": "poison"},
    {"name_ru": "Лягушка-помидор", "latin": "Dyscophus antongilii", "habitat_ru": "Мадагаскар", "fact_ru": "Надувается чтобы отпугнуть хищников", "image_url": "", "tags": "red"},
    {"name_ru": "Мшистая лягушка", "latin": "Theloderma corticale", "habitat_ru": "Вьетнам", "fact_ru": "Похожа на кусок мха", "image_url": "", "tags": "camouflage"},
    {"name_ru": "Лягушка-летяга", "latin": "Rhacophorus nigropalmatus", "habitat_ru": "Малайзия", "fact_ru": "Планирует между деревьями", "image_url": "", "tags": "glide"},
    {"name_ru": "Африканская когтистая лягушка", "latin": "Xenopus laevis", "habitat_ru": "Африка", "fact_ru": "Используется в лабораториях", "image_url": "", "tags": "lab"},
    {"name_ru": "Пустынная лягушка", "latin": "Breviceps macrops", "habitat_ru": "Намибия", "fact_ru": "Живёт под песком", "image_url": "", "tags": "desert"},
]

JOKES = [
    "Жаба сидела. Жаба думала. Жаба не придумала. Но гордится.",
    "Ква. Я хотела быть принцессой. Но стала напоминалкой про воду.",
    "Жаба нашла штангу. Штанга нашла жабу. Теперь они семья.",
    "Если ты не пил воду — ты не жаба. Ты сухарь. Ква.",
    "жаба сидела. жаба думала. жаба передумала. ква.",
]

EVENTS = [
    "Жаба сообщает: сегодня 37% шанс найти носок без пары и 100% шанс быть живым. Ква.",
    "Срочное жабо-сообщение: ты красавчик. Всё. Дальше сам.",
    "Жаба открыла философию: смысл жизни — в тёплом пруду и нормальном сне.",
    "Жаба считает до трёх: ква. ква. ква. отлично.",
]


async def seed(db_path: str, frogs_json_path: str = DEFAULT_JSON):
    db = Database(db_path)
    await db.connect()

    # 1) Frogs: спочатку JSON, якщо є і мало записів; інакше builtin
    frog_count = await db.count_frogs()
    json_file = Path(frogs_json_path)
    existing = await db.fetchall("SELECT latin FROM frog_species")
    existing_latin = {(r["latin"] or "").strip().lower() for r in existing} if existing else set()

    if frog_count < 50:
        frogs_to_add: list[dict] = []
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                frogs_to_add = json.load(f)
        if not frogs_to_add:
            frogs_to_add = BUILTIN_FROGS

        inserted = 0
        for fr in frogs_to_add:
            latin = (fr.get("latin") or "").strip()
            if not latin or latin.lower() in existing_latin:
                continue
            await db.execute(
                """INSERT INTO frog_species(name_ru, latin, habitat_ru, fact_ru, image_url, tags)
                   VALUES(?,?,?,?,?,?)""",
                (
                    fr.get("name_ru") or latin,
                    latin,
                    fr.get("habitat_ru") or "—",
                    fr.get("fact_ru") or "Ква. Реальный вид. Подробности — в энциклопедии.",
                    fr.get("image_url") or "",
                    fr.get("tags") or "anura",
                ),
            )
            existing_latin.add(latin.lower())
            inserted += 1
        if inserted:
            print(f"[seed] frogs imported: {inserted}")

    # 2) Jokes
    row = await db.fetchone("SELECT COUNT(1) AS c FROM jokes")
    if row and int(row["c"]) < 20:
        for j in JOKES:
            await db.execute("INSERT INTO jokes(text, tags) VALUES(?,?)", (j, "base"))

    # 3) Events
    row = await db.fetchone("SELECT COUNT(1) AS c FROM events")
    if row and int(row["c"]) < 20:
        for e in EVENTS:
            await db.execute("INSERT INTO events(text, tags) VALUES(?,?)", (e, "base"))

    await db.close()


if __name__ == "__main__":
    db_path = os.getenv("DB_PATH", "leinerfrog.db")
    frogs_json = os.getenv("FROGS_JSON", DEFAULT_JSON)
    asyncio.run(seed(db_path, frogs_json))
