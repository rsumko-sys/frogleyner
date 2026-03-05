"""
Генерація frog_species_200.json з GBIF + Wikipedia Summary.
Запуск: python tools/build_frog_dataset.py
Вихід: frog_species_200.json у корені проекту (або вказана директорія).
"""
import asyncio
import json
import random
import re
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("pip install aiohttp")
    raise

GBIF_BASE = "https://api.gbif.org/v1"
WIKI_SUMMARY = "https://ru.wikipedia.org/api/rest_v1/page/summary/"
UA = "LeinerFrogBot/1.0 (contact: frog@example.com)"


def slugify_wiki(title: str) -> str:
    return title.replace(" ", "_")


def extract_fact_ru(wiki: dict | None) -> str:
    if not wiki:
        return ""
    txt = (wiki.get("extract") or "").strip()
    if not txt:
        return ""
    m = re.split(r"(?<=[.!?])\s+", txt)
    return (m[0] if m else txt)[:220]


def habitat_from_gbif(profile: dict) -> str:
    return "Разные регионы (см. источники/описание вида)"


async def gbif_species_search(session: aiohttp.ClientSession, limit: int = 100, offset: int = 0):
    params = {
        "q": "Anura",
        "rank": "SPECIES",
        "status": "ACCEPTED",
        "limit": limit,
        "offset": offset,
    }
    async with session.get(f"{GBIF_BASE}/species/search", params=params) as r:
        r.raise_for_status()
        return await r.json()


async def gbif_species_profile(session: aiohttp.ClientSession, species_key: int):
    async with session.get(f"{GBIF_BASE}/species/{species_key}") as r:
        r.raise_for_status()
        return await r.json()


async def wiki_summary(session: aiohttp.ClientSession, title: str) -> dict | None:
    url = WIKI_SUMMARY + slugify_wiki(title)
    headers = {"User-Agent": UA}
    try:
        async with session.get(url, headers=headers, params={"redirect": "true"}, timeout=5) as r:
            if r.status >= 400:
                return None
            return await r.json()
    except Exception:
        return None


async def build_dataset(n: int = 200, seed_val: int = 42) -> list[dict]:
    random.seed(seed_val)
    frogs: list[dict] = []
    seen_latin: set[str] = set()
    offset = 0

    async with aiohttp.ClientSession(headers={"User-Agent": UA}) as session:
        while len(frogs) < n:
            data = await gbif_species_search(session, limit=100, offset=offset)
            results = data.get("results", [])
            if not results:
                break
            random.shuffle(results)

            for item in results:
                if len(frogs) >= n:
                    break
                key = item.get("key")
                latin = item.get("canonicalName") or item.get("scientificName") or ""
                if not key or not latin or latin in seen_latin:
                    continue
                seen_latin.add(latin)

                try:
                    prof = await gbif_species_profile(session, key)
                except Exception:
                    prof = {}
                ws = await wiki_summary(session, latin)
                name_ru = (ws.get("title") if ws and ws.get("title") else "") or latin
                fact = extract_fact_ru(ws) if ws else ""
                if not fact:
                    fact = "Ква. Реальный вид лягушек/жаб; подробности см. в энциклопедии."

                frogs.append({
                    "name_ru": name_ru,
                    "latin": latin,
                    "habitat_ru": habitat_from_gbif(prof),
                    "fact_ru": fact,
                    "image_url": "",
                    "tags": "anura",
                })
                await asyncio.sleep(0.05)

            offset += 100
            await asyncio.sleep(0.2)

    return frogs


async def main():
    out_path = Path(__file__).resolve().parent / "frog_species_200.json"
    frogs = await build_dataset(n=200)
    print(f"Generated: {len(frogs)} frogs")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(frogs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
