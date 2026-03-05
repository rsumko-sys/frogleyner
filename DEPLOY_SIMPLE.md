# Найпростіший деплой (5 хвилин)

## Railway — без конфігів, тільки репо + токен

---

## 🆘 Вже бачиш список проєктів і одне "0/1 service online"?

Якщо на твоєму дашборді виглядає так:

```
robust-kindness          — No services
superb-benevolence       — No services
dynamic-recreation       — No services
diplomatic-gentleness    — production · 0/1 service online   ← ЦЕ ТВІЙ
honest-empathy           — No services
```

**→ Клікни на той проєкт, де написано `0/1 service online`** (наприклад `diplomatic-gentleness`).

Це твій проєкт із задеплоєним ботом. Він офлайн тому, що **ще не задано `BOT_TOKEN`** — без нього бот падає одразу при старті.

### Що робити далі (3 кліки):

1. **Клікни на проєкт** `diplomatic-gentleness` (або той, де `0/1 service online`).
2. На canvas (полотні всередині проєкту) побачиш **картку сервісу** (прямокутник із назвою репо або `frogbot`). **Клікни на картку**.
3. Відкриється бічна панель із вкладками:
   ```
   Deployments  ·  Logs  ·  Variables  ·  Settings
   ```
4. Клікни **Variables** → **`+ New Variable`**:
   - **Name:** `BOT_TOKEN`
   - **Value:** токен від @BotFather (щось на зразок `7123456789:AAF_abc...`)
5. Натисни **Add** — Railway перезапустить бота автоматично (~30 сек).
6. Клікни вкладку **Logs** — маєш побачити:
   ```
   === Frog bot: polling started ===
   ```
   Якщо це є — бот живий ✅

> **Чому сервіс офлайн?** Код перевіряє `BOT_TOKEN` одразу при старті.  
> Якщо змінна не задана — бот падає з помилкою `RuntimeError: BOT_TOKEN is not set`.  
> Щойно додаєш токен — сервіс піднімається.

---

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

3. **Де знайти Variables (BOT_TOKEN)**

   > ⚠️ **Важливо:** Variables — це НЕ в меню зліва і не в Project Settings.  
   > Вона всередині самого сервісу, по центру сторінки.

   Точний маршрут:
   1. Відкрий свій проєкт на [railway.app](https://railway.app/dashboard).
   2. На canvas (полотні) побачиш картку сервісу (наприклад `frogbot`). **Клікни на неї**.
   3. Відкриється панель сервісу з вкладками вгорі:  
      `Deployments` · `Logs` · **`Variables`** · `Settings`
   4. Клікни **Variables**.
   5. Клікни **`+ New Variable`** (або **`Raw Editor`** для швидкого вставлення).
   6. Заповни:
      - **Name:** `BOT_TOKEN`
      - **Value:** токен від @BotFather (виглядає як `123456789:AAF...`)
   7. Натисни **Add** → Railway автоматично перезапустить деплой.

   ✅ Якщо вкладки не видно — переконайся, що ти клікнув саме **на картку сервісу**, а не на фон проєкту.

4. **Команда запуску (Start Command)**  
   Вкладка **Settings** (в тій же панелі сервісу) → розділ **Deploy**:
   - **Start Command:** `python main.py`  
   Збережи. Railway перезадеплоїть бота.

5. Готово. Бот працює 24/7. Логи — вкладка **Deployments** → **View Logs**.

---

**Примітка:** На безкоштовному плані Railway дає обмежений кредит на місяць. Якщо вичерпається — можна перейти на Render (див. DEPLOY.md) або додати картку в Railway.
