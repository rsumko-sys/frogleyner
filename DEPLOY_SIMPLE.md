
# Найпростіший деплой (5 хвилин)

## Railway — без конфігів, тільки репо + токен

1. **Репо на GitHub**  
   Якщо ще немає:
   ```bash
   cd /Users/admin/frogbot
   git init
   git add .
   git commit -m "bot"
   ```
   На [github.com](https://github.com) створи новий репо (наприклад `frogbot`), потім:
   ```bash
   git remote add origin https://github.com/TVІЙ_LOGIN/frogbot.git
   git branch -M main
   git push -u origin main
   ```

2. **Railway**  
   - Зайди на [railway.app](https://railway.app), увійди через GitHub.
   - **New Project** → **Deploy from GitHub repo** → вибери репо `frogbot`.


3. **Змінні**  
   Знайди правильний Railway-проєкт (той, де 0/1 service online — це твій бот).
   Відкрий сервіс (натисни на прямокутник/box на canvas).
   Перейди у вкладку **Variables** → **Add Variable**:
   - Name: `BOT_TOKEN`
   - Value: твій токен від @BotFather
   Натисни Add — Railway автоматично перезапустить сервіс (~30 секунд).

4. **Перевірка**
   Перейди у вкладку **Logs** (або **Deployments** → **View Logs**).
   Якщо бачиш `=== Frog bot: polling started ===`, бот працює ✅

5. **Збереження бази даних**
   Файлова система Railway тимчасова — SQLite база видаляється при кожному рестарті/деплої.
   Щоб зберегти дані:
   - Відкрий сервіс → вкладка **Settings**
   - Прокрути до **Storage / Volumes**
   - **Add Volume** → Mount Path: `/data` → Save
   - Перейди у вкладку **Variables** → **Add Variable**:
     - Name: `DB_PATH`
     - Value: `/data/leinerfrog.db`
   - Натисни Add — Railway перезапустить сервіс, і база буде збережена 💾


6. **Команда запуску**  
   Вкладка **Settings** → **Deploy**:
   - **Start Command:** `python seed.py && python main.py`  
   Збережи. Railway перезадеплоїть бота.

7. Готово. Бот працює 24/7. Логи — вкладка **Deployments** → **View Logs**.

---

**Примітка:** На безкоштовному плані Railway дає обмежений кредит на місяць. Якщо вичерпається — можна перейти на Render (див. DEPLOY.md) або додати картку в Railway.
