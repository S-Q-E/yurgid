import os
import httpx
from openai import AsyncOpenAI
from prompts import AGENT_PROMPT
from search import search_adilet
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиента OpenAI с кастомным http_client
custom_client = httpx.AsyncClient(proxies=None)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=custom_client)

def adilet_search_tool(query: str) -> str:
    """Инструмент, который ищет на adilet.zan.kz и форматирует результат."""
    try:
        results = search_adilet(query)
        if not results or isinstance(results, str):
            return "По вашему запросу на adilet.zan.kz ничего не найдено."
        
        output = ""
        for r in results:
            output += f"Заголовок: {r.get('title', 'Без заголовка')}\n"
            output += f"Ссылка: {r.get('link', 'Нет ссылки')}\n"
            output += f"Фрагмент: {r.get('snippet', 'Нет фрагмента')}\n---\n"
        return output
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

async def run_agent(query: str, history: list) -> str:
    """Выполняет поиск и генерирует ответ с помощью OpenAI, учитывая историю диалога."""
    try:
        # 1. Выполняем поиск
        search_results = adilet_search_tool(query)

        # 2. Составляем промпт для модели
        system_prompt = AGENT_PROMPT
        user_prompt = f"""
        Пользовательский запрос: "{query}"

        Вот результаты поиска по adilet.zan.kz:
        ---
        {search_results}
        ---

        Основываясь на этих результатах, своих знаниях и предыдущем контексте диалога, дай ответ на запрос, 
        строго следуя правилам из системного промпта.
        """

        # 3. Формируем сообщения для модели, включая историю
        messages_to_send = [{"role": "system", "content": system_prompt}]
        messages_to_send.extend(history)
        messages_to_send.append({"role": "user", "content": user_prompt})


        # 4. Вызываем модель
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send,
            temperature=0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Ошибка работы агента: {str(e)}"

async def improve_answer(answer: str) -> str:
    """Запрашивает у модели рекомендации по улучшению ответа."""
    prompt = f"""
    Ты — юридический консультант по законодательству Казахстана.
    Пользователь получил следующий ответ: 

    {answer}

    Дай рекомендации, какие дополнительные детали, документы или уточнения 
    может предоставить пользователь, чтобы сделать ответ точнее и полезнее.
    Не переписывай сам ответ, только предложи, что уточнить.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка улучшения: {str(e)}"


