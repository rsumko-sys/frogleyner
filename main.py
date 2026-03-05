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
    def __init__(self, db: Database):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db"] = self.db
        return await handler(event, data)


async def main():
    print("=== Frog bot: starting ===", flush=True)
    cfg = load_config()
    print(f"=== Config loaded (db={cfg.db_path}) ===", flush=True)
    db = Database(cfg.db_path)
    await db.connect()
    await seed_db(cfg.db_path)
    print("=== DB ready ===", flush=True)

    bot = Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.update.middleware(DbMiddleware(db))
    dp.include_router(router)

    sched = build_scheduler(bot, db)
    sched.start()
    print("=== Scheduler started ===", flush=True)

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
        BotCommand(command="fortune", description="Предсказание"),
        BotCommand(command="status", description="Статус бота"),
        BotCommand(command="ping", description="Проверка связи"),
        BotCommand(command="mute", description="Выключить авто-сообщения"),
        BotCommand(command="unmute", description="Включить авто-сообщения"),
        BotCommand(command="secret", description="Секрет болота"),
    ]
    await bot.set_my_commands(commands_ru)

    # Remove any existing webhook so updates come via polling
    await bot.delete_webhook(drop_pending_updates=True)
    print("=== Frog bot: polling started ===", flush=True)

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
        import traceback
        print(f"=== Frog bot CRASH: {e} ===", flush=True)
        traceback.print_exc()
        raise
