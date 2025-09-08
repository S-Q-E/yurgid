# main.py
import asyncio
from bot import dp, bot
from handlers import router
from database import Base, engine
from logger import setup_logger

log = setup_logger()

async def main():
    # Создаем таблицы асинхронно
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp.include_router(router)
    log.info("Bot started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())