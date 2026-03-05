# Жаба Лейнера (LeinerFrog)

Telegram-бот на Python 3.11+: aiogram v3, APScheduler, SQLite (aiosqlite).

## Запуск

### Варіант A: локально (Python)

1. Створи бота в [@BotFather](https://t.me/BotFather), отримай токен.

2. Скопіюй `.env.example` → `.env` і встав токен:
   ```bash
   cp .env.example .env
   # Відкрий .env і заміни BOT_TOKEN на реальний
   ```

3. Встанови залежності, заповни БД і запусти бота одним командою:
   ```bash
   make run
   ```
   Або покроково:
   ```bash
   pip install -r requirements.txt
   python seed.py
   python main.py
   ```

4. (Опційно) Згенеруй 200 жаб з GBIF + Wikipedia:
   ```bash
   python build_frog_dataset.py
   ```
   Створиться `frog_species_200.json`, який `seed.py` підхопить автоматично.

### Варіант B: Docker Compose

```bash
cp .env.example .env   # заповни BOT_TOKEN
docker compose up -d   # збирає образ і запускає у фоні
docker compose logs -f # стеж за логами
```

### Варіант C: Docker (вручну)

```bash
docker build -t leinerfrog .
docker run --rm --env-file .env -e DB_PATH=/data/leinerfrog.db \
    -v leinerfrog-data:/data leinerfrog
```

## Тестування

```bash
make test
# або
python -m pytest tests/ -v
```

## Деплой у хмару

- Render / Railway — дивись **DEPLOY.md** / **DEPLOY_SIMPLE.md**.
- Docker на VPS — дивись **DOCKER.md**.

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
| `/fortune` | Передбачення |
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
- `build_frog_dataset.py` — генерація frog_species_200.json (GBIF + Wikipedia)  
- `Makefile` — зручні цілі: `install`, `run`, `test`, `docker`, `docker-run`  
- `docker-compose.yml` — запуск через Docker Compose  

## База даних

- **users**: user_id, tz, autopush, weight_kg, friendship_level, annoyance, care_mode, created_at, last_seen  
- **water_log**, **training_log** — логи води та тренувань  
- **frog_species**, **frog_day** — жаба дня  
- **jokes**, **events** — контент  
- **reactions** — логи реакцій (👍/🤨/💀)
