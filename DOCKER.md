# Запуск бота через Docker

## 1. Локально

### Docker Compose (найпростіше)

```bash
cp .env.example .env   # заповни BOT_TOKEN
docker compose up -d   # збирає образ і запускає у фоні
docker compose logs -f # стеж за логами
docker compose down    # зупинити
```

База зберігається у тому `frogdata` між перезапусками.

### Docker вручну

Збірка образу:
```bash
cd frogleyner
docker build -t leinerfrog .
```

Запуск (токен передаємо змінною):
```bash
docker run --rm -e BOT_TOKEN="ТВІЙ_ТОКЕН" leinerfrog
```

Щоб база зберігалась між перезапусками — монтуй том:
```bash
docker run --rm \
    -e BOT_TOKEN="ТВІЙ_ТОКЕН" \
    -e DB_PATH=/data/leinerfrog.db \
    -v leinerfrog-data:/data \
    leinerfrog
```

---

## 2. Деплой в хмару через Docker

### Варіант A: Railway (найпростіше)

1. **Репо на GitHub**  
   - Репо містить `Dockerfile` і `main.py` в корені — просто пуши.

2. **Railway**  
   - Зайди на [railway.app](https://railway.app), увійди через GitHub.  
   - **New Project** → **Deploy from GitHub repo** → вибери репо.  
   - Railway сам визначить Docker і збере образ. Старт уже в `Dockerfile` (`CMD`).

3. **Змінні**  
   У проєкті: **Variables** → **Add Variable** → `BOT_TOKEN` = токен від @BotFather. Збережи — Railway перезадеплоїть контейнер.

4. Готово. Логи: **Deployments** → **View Logs**.

### Варіант B: Render (Docker)

1. Репо на GitHub з `Dockerfile` у корені.
2. [render.com](https://render.com) → **New** → **Background Worker**.
3. Підключи репо. У **Environment** вибери **Docker** (Render використає твій Dockerfile).
4. **Environment Variables**: додай `BOT_TOKEN` (Secret).
5. **Create** — Render збере образ і запустить контейнер. Старт з `CMD` у Dockerfile.

### Варіант C: VPS (свій сервер)

На сервері з Docker:
```bash
git clone <твій-репо> && cd frogleyner
docker build -t leinerfrog .
docker run -d --restart unless-stopped \
    -e BOT_TOKEN="..." \
    -e DB_PATH=/data/leinerfrog.db \
    -v leinerfrog-data:/data \
    --name frogbot leinerfrog
```
`-d` — у фоні, `--restart unless-stopped` — автоперезапуск після перезавантаження сервера.
