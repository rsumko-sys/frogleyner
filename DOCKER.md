# Запуск бота через Docker

## 1. Локально

Збірка образу:
```bash
cd /Users/admin/frogbot
docker build -t leinerfrog .
```

Запуск (токен передаємо змінною):
```bash
docker run --rm -e BOT_TOKEN="ТВІЙ_ТОКЕН" leinerfrog
```

Щоб база зберігалась між перезапусками — монтуй том:
```bash
docker run --rm -e BOT_TOKEN="ТВІЙ_ТОКЕН" -v frogbot-data:/app leinerfrog
```
База буде в тому `frogbot-data`.

---

## 2. Деплой в хмару через Docker

### Варіант A: Railway (найпростіше)

1. **Репо на GitHub**  
   - Якщо репо містить тільки вміст frogbot (у корені є `Dockerfile`, `main.py`) — просто пуши.  
   - Якщо frogbot — це папка всередині великого репо: на Railway в налаштуваннях сервісу вкажи **Root Directory** = `frogbot`, щоб збірка йшла з цієї папки.

2. **Railway**  
   - Зайди на [railway.app](https://railway.app), увійди через GitHub.  
   - **New Project** → **Deploy from GitHub repo** → вибери репо (той, де в корені є `Dockerfile` і `main.py`).  
   - Railway сам визначить Docker і збере образ. Старт уже в `Dockerfile` (`CMD`).

3. **Змінні**  
   У проєкті: **Variables** → **Add Variable** → `BOT_TOKEN` = токен від @BotFather. Збережи — Railway перезадеплоїть контейнер.

4. Готово. Логи: **Deployments** → **View Logs**.

### Варіант B: Render (Docker)

1. Репо на GitHub з `Dockerfile` у корені (або у папці, яку вкажеш як Root Directory).
2. [render.com](https://render.com) → **New** → **Background Worker**.
3. Підключи репо. У **Environment** вибери **Docker** (Render використає твій Dockerfile).
4. **Environment Variables**: додай `BOT_TOKEN` (Secret).
5. **Create** — Render збере образ і запустить контейнер. Старт з `CMD` у Dockerfile.

### Варіант C: VPS (свій сервер)

На сервері з Docker:
```bash
git clone <твій-репо> && cd frogbot   # або скопіюй папку frogbot
docker build -t leinerfrog .
docker run -d --restart unless-stopped -e BOT_TOKEN="..." -v frogbot-data:/app --name frogbot leinerfrog
```
`-d` — у фоні, `--restart unless-stopped` — автоперезапуск після перезавантаження сервера.
