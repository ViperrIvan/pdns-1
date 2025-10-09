import re
import random
from time import sleep
from typing import Tuple, List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageScout:
    """Класс-разведчик для определения количества страниц"""

    def __init__(self):
        self.driver = None
        self.xpathes = {
            "pagination": "//div[contains(@class, 'pagination-widget')]//a",
            "last_page": "//div[contains(@class, 'pagination-widget')]//a[contains(@class, 'pagination-widget__page-link_last')]",
            "page_numbers": "//div[contains(@class, 'pagination-widget')]//a[contains(@class, 'pagination-widget__page-link')]",
            "product_count": "//div[contains(@class, 'products-count')]",
        }

    def get_total_pages(self, url: str) -> int:
        """Определяет общее количество страниц для парсинга"""
        try:
            from .parser import BrowserManager
            self.driver = BrowserManager.start_browser()
            self.driver.get(url)
            sleep(random.uniform(3, 6))

            # Пробуем разные методы определения количества страниц
            total_pages = self._try_pagination_methods()

            if total_pages == 0:
                total_pages = self._estimate_from_product_count()

            print(f"Определено страниц для парсинга: {total_pages}")
            return max(1, total_pages)

        except Exception as e:
            print(f"Ошибка при определении количества страниц: {e}")
            return 1
        finally:
            if self.driver:
                self.driver.quit()

    def _try_pagination_methods(self) -> int:
        """Пробует разные методы определения пагинации"""
        methods = [
            self._get_from_last_page_button,
            self._get_from_page_numbers,
            self._get_from_pagination_links,
        ]

        for method in methods:
            try:
                result = method()
                if result > 0:
                    return result
            except Exception:
                continue

        return 0

    def _get_from_last_page_button(self) -> int:
        """Получает номер последней страницы из кнопки 'последняя'"""
        try:
            last_page_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.xpathes["last_page"]))
            )
            last_page_text = last_page_element.text.strip()
            return int(last_page_text) if last_page_text.isdigit() else 0
        except:
            return 0

    def _get_from_page_numbers(self) -> int:
        """Получает максимальный номер страницы из всех номеров"""
        try:
            page_elements = self.driver.find_elements(By.XPATH, self.xpathes["page_numbers"])
            page_numbers = []

            for element in page_elements:
                try:
                    text = element.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                except:
                    continue

            return max(page_numbers) if page_numbers else 0
        except:
            return 0

    def _get_from_pagination_links(self) -> int:
        """Анализирует все ссылки пагинации"""
        try:
            pagination_elements = self.driver.find_elements(By.XPATH, self.xpathes["pagination"])
            max_page = 0

            for element in pagination_elements:
                try:
                    href = element.get_attribute("href")
                    if href and "p=" in href:
                        match = re.search(r'p=(\d+)', href)
                        if match:
                            page_num = int(match.group(1))
                            max_page = max(max_page, page_num)

                    text = element.text.strip()
                    if text.isdigit():
                        max_page = max(max_page, int(text))

                except Exception:
                    continue

            return max_page
        except:
            return 0

    def _estimate_from_product_count(self) -> int:
        """Оценивает количество страниц по общему числу товаров"""
        try:
            count_element = self.driver.find_element(By.XPATH, self.xpathes["product_count"])
            count_text = count_element.text.strip()

            match = re.search(r'(\d+)\s*из\s*(\d+)', count_text)
            if match:
                total_products = int(match.group(2))
                return max(1, (total_products + 19) // 20)
        except:
            pass

        return 5


class TaskDistributor:
    """Распределяет задачи по страницам между потоками"""

    @staticmethod
    def distribute_pages(total_pages: int, num_threads: int) -> List[Tuple[int, int]]:
        """Распределяет страницы между потоками"""
        if total_pages <= 0 or num_threads <= 0:
            return [(1, 1)]

        num_threads = min(num_threads, total_pages)
        pages_per_thread = total_pages // num_threads
        remainder = total_pages % num_threads

        distributions = []
        start_page = 1

        for i in range(num_threads):
            extra_page = 1 if i < remainder else 0
            end_page = start_page + pages_per_thread + extra_page - 1
            distributions.append((start_page, end_page))
            start_page = end_page + 1

        print(f"Распределение страниц между {num_threads} потоками: {distributions}")
        return distributions

    @staticmethod
    def generate_page_urls(base_url: str, start_page: int, end_page: int) -> List[str]:
        """Генерирует URL для диапазона страниц"""
        urls = []

        for page in range(start_page, end_page + 1):
            if "?" in base_url:
                url = f"{base_url}&p={page}"
            else:
                url = f"{base_url}?p={page}"
            urls.append(url)

        return urls