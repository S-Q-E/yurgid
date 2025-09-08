from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import engine, Base
from models import User, Session, Message

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import run_agent, improve_answer
from utils import get_or_create_user, create_user_session, save_message
from logger import setup_logger

# --- Настройка логгера ---
log = setup_logger()


async def init_database():
    """Инициализирует базу данных: создает таблицы, если их нет."""
    async with engine.begin() as conn:
        # create_all не удаляет и не изменяет существующие таблицы,
        # а только создает недостающие.
        await conn.run_sync(Base.metadata.create_all)
    log.info("База данных проверена и готова к работе.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, который выполнится при старте приложения
    log.info("Запуск приложения...")
    await init_database()

    yield  # В этот момент приложение начинает работать и принимать запросы

    # Код, который выполнится при остановке приложения
    log.info("Остановка приложения...")
    # Здесь можно, например, корректно закрыть соединения
    await engine.dispose()


# --- FastAPI приложение ---

app = FastAPI(
    title="ЮрГид KZ API",
    description="API для юридического помощника по законодательству Казахстана.",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем статическую директорию для CSS и JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Модели для API ---
class ChatRequest(BaseModel):
    prompt: str
    session_id: int

class ImproveRequest(BaseModel):
    answer: str

# --- API эндпоинты ---

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Отдает главную HTML страницу чата."""
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/start_session")
async def start_session():
    """Создает пользователя (если его нет) и новую сессию."""
    log.info("Attempting to start a new session...")
    try:
        # Для веб-интерфейса используем "гостевого" пользователя
        user = await get_or_create_user(telegram_id=0, username="web_guest")
        session_id = await create_user_session(user.id)
        log.info(f"Successfully created session {session_id} for user {user.id}")
        return JSONResponse(content={"session_id": session_id})
    except Exception as e:
        log.error(f"Failed to start session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """Принимает запрос, сохраняет его, получает ответ и тоже сохраняет."""
    try:
        # 1. Сохраняем сообщение пользователя
        await save_message(
            session_id=chat_request.session_id, 
            text=chat_request.prompt, 
            is_user=True
        )

        # 2. Получаем ответ от агента
        response_text = await run_agent(chat_request.prompt)

        # 3. Сохраняем ответ агента
        await save_message(
            session_id=chat_request.session_id, 
            text=response_text, 
            is_user=False
        )

        return JSONResponse(content={"response": response_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/improve")
async def improve_endpoint(improve_request: ImproveRequest):
    """Принимает ответ и возвращает рекомендации по его улучшению."""
    try:
        improved_text = await improve_answer(improve_request.answer)
        return JSONResponse(content={"response": improved_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

