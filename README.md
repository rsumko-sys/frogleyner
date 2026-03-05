# Жаба Лейнера (LeinerFrog)

Telegram-бот на Python 3.11+: aiogram v3, APScheduler, SQLite (aiosqlite).

## Запуск

1. Створи бота в [@BotFather](https://t.me/BotFather), отримай токен.

2. Встанови залежності:
   ```bash
   pip install -r requirements.txt
   ```

3. Скопіюй `.env.example` → `.env` і встав токен:
   ```bash
   cp .env.example .env
   # Відкрий .env і заміни BOT_TOKEN на реальний
   ```

4. (Опційно) Згенеруй 200 жаб з GBIF + Wikipedia:
   ```bash
   python build_frog_dataset.py
   ```
   Створиться `frog_species_200.json`.

5. Seed БД (жаби, жарти, події):
   ```bash
   python seed.py
   ```

6. Запуск бота:
   ```bash
   python main.py
   ```

## Тестування

```bash
pip install pytest
python -m pytest tests/ -v
```

## Команди

| Команда | Опис |
|--------|------|
| `/start` | Реєстрація, автопуш увімкнено |
| `/help` | Список команд |
| `/frog` | Випадкова репліка |
| `/frogday` | Жаба дня (одна на добу) |
| `/water` | Вода сьогодні + % жабности |
| `/drink` | +250 мл води |
| `/protein 80` | Білок на день (2 г/кг) |
| `/setweight 80` | Встановити вагу для розрахунку води |
| `/joke` | Марковський жарт |
| `/mute` | Вимкнути авто-повідомлення |
| `/unmute` | Увімкнути авто-повідомлення |

## Розклад (Europe/Kyiv)

- 07:30 — ранок  
- 09:00 — вода (кнопка «Я випив 250 мл»)  
- 13:00 — їжа  
- 16:00 — випадкова подія (іноді пропуск)  
- 19:00 — зал (кнопки «Так» / «Ні»)  
- 22:30 — сон  

Додатково: «brain tick» кожні 45–120 хв (випадково), перевірка тиші раз на 12 год (check-in після 2/3/5 днів без відповіді).

## Структура

- `main.py` — вхід, polling, scheduler  
- `config.py` — BOT_TOKEN, DB_PATH  
- `db.py` — SQLite, таблиці users/water_log/training_log/frog_species/frog_day/jokes/events/reactions  
- `handlers.py` — команди та callback (вода, зал, реакції)  
- `scheduler.py` — cron + brain tick + silence check  
- `frog_brain.py` — настрій, дружба, burst, check-in  
- `seed.py` — імпорт жаб (JSON або вбудований список), жарти, події  
- `content/frog_texts.py` — тексти пингів  
- `content/leiner_quotes_ru.py` — репліки за настроєм  
- `content/markov.py` — MarkovNgram для /joke  
- `tools/build_frog_dataset.py` — генерація frog_species_200.json (GBIF + Wikipedia)

## База даних

- **users**: user_id, tz, autopush, weight_kg, friendship_level, annoyance, care_mode, created_at, last_seen  
- **water_log**, **training_log** — логи води та тренувань  
- **frog_species**, **frog_day** — жаба дня  
- **jokes**, **events** — контент  
- **reactions** — логи реакцій (👍/🤨/💀)
