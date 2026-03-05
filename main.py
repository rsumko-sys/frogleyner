import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject, BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from config import load_config
from db import Database
from seed import seed as seed_db
from handlers import router
from scheduler import build_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class DbMiddleware(BaseMiddleware):
    def __init__(self, db: Database, host_user_id: int = 0):
        self.db = db
        self.host_user_id = host_user_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db"] = self.db
        data["host_user_id"] = self.host_user_id
        return await handler(event, data)


async def main():
    print("Frog bot: starting...", flush=True)
    cfg = load_config()
    print("Frog bot: config loaded", flush=True)
    db = Database(cfg.db_path)
    await db.connect()
    await seed_db(cfg.db_path)

    bot = Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.update.middleware(DbMiddleware(db, host_user_id=cfg.host_user_id))
    dp.include_router(router)

    sched = build_scheduler(
        bot,
        db,
        openweather_api_key=cfg.openweather_api_key,
        weather_city=cfg.weather_city,
        host_user_id=cfg.host_user_id,
    )
    sched.start()

    commands_ru = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Справка по командам"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="frog", description="Случайная реплика жабы"),
        BotCommand(command="frogday", description="Жаба дня"),
        BotCommand(command="water", description="Вода и % жабности"),
        BotCommand(command="drink", description="Выпил 250 мл"),
        BotCommand(command="protein", description="Белок на день"),
        BotCommand(command="setweight", description="Вес для расчёта воды"),
        BotCommand(command="joke", description="Шутка"),
        BotCommand(command="fact", description="Факт про жаб і болото"),
        BotCommand(command="fortune", description="Предсказание"),
        BotCommand(command="status", description="Статус бота"),
        BotCommand(command="ping", description="Проверка связи"),
        BotCommand(command="mute", description="Выключить авто-сообщения"),
        BotCommand(command="unmute", description="Включить авто-сообщения"),
        BotCommand(command="secret", description="Секрет болота"),
    ]
    await bot.set_my_commands(commands_ru)

    # Якщо десь був webhook — знімаємо, щоб оновлення йшли в polling
    await bot.delete_webhook(drop_pending_updates=True)

    print("Frog bot: polling started", flush=True)
    try:
        await dp.start_polling(bot)
    finally:
        sched.shutdown(wait=False)
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Frog bot CRASH: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise
