# Деплой жаби в хмару (24/7)

Бот можна запускати безкоштовно на **Render** або **Railway**. Обидва дають worker, що працює постійно.

---

## Варіант 1: Render (безкоштовно)

1. **Репо на GitHub**  
   Залей проєкт у репозиторій (якщо ще не зробив):
   ```bash
   cd frogleyner
   git init
   git add .
   git commit -m "LeinerFrog bot"
   git remote add origin https://github.com/YOUR_USERNAME/frogleyner.git
   git push -u origin main
   ```
   Можна створити репо на github.com і підставити свій URL.

2. **Render**  
   - Зайди на [render.com](https://render.com), зареєструйся (GitHub).
   - **Dashboard** → **New** → **Blueprint**.
   - Підключи репо з frogbot, у полі **Blueprint** має підтягнутися `render.yaml`.
   - Натисни **Apply**.

3. **Секрет BOT_TOKEN**  
   - Відкрий створений сервіс **leinerfrog-bot**.
   - **Environment** → **Add Environment Variable**:
     - Key: `BOT_TOKEN`
     - Value: твій токен від @BotFather (можна позначити як **Secret**).
   - Збережи. Render перезапустить бота.

4. **Перевірка**  
   У **Logs** має з’явитися щось на кшталт `Run polling for bot @jabavlafabot`. Напиши боту в Telegram — має відповідати.

**Примітка:** На безкоштовному плані SQLite живе в тимчасовому середовищі: після перезапуску/редеплою база скидається (користувачі та логи). Для постійного збереження даних можна пізніше увімкнути **Disk** (платно) і в `render.yaml` додати `disk` + змінити `DB_PATH` на шлях у цьому диску.

---

## Варіант 2: Railway (безкоштовний кредит)

1. **Репо на GitHub** — так само, як для Render.

2. **Railway**  
   - [railway.app](https://railway.app) → увійти через GitHub.
   - **New Project** → **Deploy from GitHub repo** → вибери репо з frogbot.

3. **Налаштування сервісу**  
   - Відкрий створений сервіс → **Settings** (або **Variables**).
   - **Variables** → додай:
     - `BOT_TOKEN` = твій токен.
     - За бажанням: `DB_PATH` = `leinerfrog.db`.
   - **Settings** → **Deploy**:
     - **Build Command:** `pip install -r requirements.txt` (або залишити авто).
     - **Start Command:** `python seed.py && python main.py`.
   - Збережи. Railway перезадеплоїть бота.

4. **Перевірка**  
   У **Deployments** → **View Logs** має бути запуск бота. Напиши боту в Telegram.

---

## Що потрібно в репо

- У репо обов’язково мають бути: `main.py`, `config.py`, `db.py`, `handlers.py`, `scheduler.py`, `frog_brain.py`, `seed.py`, `content/`, `requirements.txt`, `render.yaml`.
- Файл **`.env`** не потрібно комітити (додай у `.gitignore`). Токен задається тільки в хмарному середовищі (Render Environment / Railway Variables).

Якщо хочеш, можу допомогти скласти `.gitignore` або перевірити, що саме пушити в репо.
