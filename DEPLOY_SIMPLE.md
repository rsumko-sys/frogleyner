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
   У проєкті відкрий сервіс → вкладка **Variables** → **Add Variable**:
   - `BOT_TOKEN` = токен від @BotFather  
   Збережи (деплой піде автоматично).

4. **Команда запуску**  
   Вкладка **Settings** → **Deploy**:
   - **Start Command:** `python seed.py && python main.py`  
   Збережи. Railway перезадеплоїть бота.

5. Готово. Бот працює 24/7. Логи — вкладка **Deployments** → **View Logs**.

---

**Примітка:** На безкоштовному плані Railway дає обмежений кредит на місяць. Якщо вичерпається — можна перейти на Render (див. DEPLOY.md) або додати картку в Railway.
