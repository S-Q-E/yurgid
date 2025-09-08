from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()


def search_adilet(query):
    """Поиск по adilet.zan.kz через Tavily Search API."""
    try:
        # Инициализация клиента Tavily
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        # Выполнение поиска, ограниченного adilet.zan.kz
        response = client.search(
            query=query,
            search_depth="basic",  # Используем basic для экономии кредитов
            max_results=3,  # Ограничение на 3 результата
            include_domains=["adilet.zan.kz"]  # Только adilet.zan.kz
        )

        # Извлечение результатов
        search_results = []
        for item in response.get("results", []):
            search_results.append({
                "title": item.get("title", "No title"),
                "link": item.get("url", "No URL"),
                "snippet": item.get("content", "No content")
            })

        return search_results
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"