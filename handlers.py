from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from agent import run_agent
import logging

router = Router()

# Временное хранилище для истории диалогов
chat_histories = {}

class Dialog(StatesGroup):
    active = State()

def get_main_kb():
    kb = [
        [KeyboardButton(text="Новый диалог")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in chat_histories:
        chat_histories[user_id] = []
    await state.clear()
    await message.answer("Привет! Я юридический помощник по законам Казахстана. Напиши свой вопрос.", reply_markup=get_main_kb())

@router.message(F.text == "Новый диалог")
async def new_dialog(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in chat_histories:
        chat_histories[user_id] = []
    await state.clear()
    await message.answer("Диалог сброшен. Можете задавать новый вопрос.")

@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    await message.answer("Обрабатываю...")
    user_id = message.from_user.id

    # Получаем историю или создаем новую
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    
    history = chat_histories[user_id]

    try:
        # Передаем в агент и текст, и историю
        answer = await run_agent(message.text, history)
        
        # Обновляем историю
        history.append({"role": "user", "content": message.text})
        history.append({"role": "assistant", "content": answer})

        # Ограничиваем размер истории, чтобы не превышать лимит токенов (например, 10 последних сообщений)
        chat_histories[user_id] = history[-10:]

        await message.answer(answer, reply_markup=get_main_kb())
        logging.info(f"User: {message.text}\nBot: {answer}")
    except Exception as e:
        await message.answer("Ошибка: попробуйте позже.")
        logging.error(f"Agent error: {e}")

# TODO: команды администратора
@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer("Юргид ваш помощник по юр вопросам")