from database import AsyncSessionLocal
from models import User, Session, Message
from sqlalchemy.future import select
from logger import setup_logger

log = setup_logger()


async def get_or_create_user(telegram_id: int, username: str) -> User:
    """
    Получает пользователя по telegram_id или создает нового, если он не найден.
    """
    log.info(f"Getting or creating user with telegram_id={telegram_id}")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            if user is None:
                log.info(f"User with telegram_id={telegram_id} not found. Creating new user.")
                user = User(telegram_id=telegram_id, username=username)
                session.add(user)
                await session.flush()
                await session.refresh(user)
                log.info(f"Created new user with id={user.id}")
            else:
                log.info(f"Found existing user with id={user.id}")
            return user


async def create_user_session(user_id: int) -> int:
    """
    Создает новую сессию для пользователя.
    """
    log.info(f"Creating new session for user_id={user_id}")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            new_session = Session(user_id=user_id)
            session.add(new_session)
            await session.flush()
            await session.refresh(new_session)
            log.info(f"Created new session with id={new_session.id}")
            return new_session.id


async def save_message(session_id: int, text: str, is_user: bool):
    """
    Сохраняет сообщение в базу данных.
    """
    log.info(f"Saving message for session_id={session_id}")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            new_message = Message(session_id=session_id, text=text, is_user=is_user)
            session.add(new_message)
            await session.flush()
            log.info(f"Saved message with id={new_message.id}")


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session