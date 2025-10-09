import sys
import os

# Добавляем путь к src в PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.thread_manager import AdvancedThreadedScraper
from src.utils.config import Config


def main():
    """Простая функция для тестирования"""
    print("🤖 Тестирование умного парсера DNS-Shop")

    try:
        scraper = AdvancedThreadedScraper(max_workers=2)

        # Тестируем только один компонент для начала
        test_urls = {
            'ram': Config.URLS['ram']
        }

        results = scraper.scrape_all(test_urls)
        print(f"✅ Успешно собрано данных: {len(results)} компонентов")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()