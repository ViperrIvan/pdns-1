from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import Dict, List, Tuple
import time


class AdvancedThreadedScraper:
    """Продвинутый многопоточный скрапер с распределением страниц"""

    def __init__(self, max_workers=3, requests_per_minute=30):
        self.max_workers = max_workers
        self.requests_per_minute = requests_per_minute
        self.results = {}
        self.lock = threading.Lock()
        self.last_request_time = 0
        self.request_lock = threading.Lock()

    def rate_limit(self):
        """Контроль скорости запросов"""
        with self.request_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            min_interval = 60.0 / self.requests_per_minute

            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)

            self.last_request_time = time.time()

    def scrape_page_range(self, component: str, page_range: Tuple[int, int], base_url: str, proxies: list[str]) -> List[Dict]:
        """Парсинг диапазона страниц для одного компонента"""
        try:
            from .parser import DNSScraper, ParserFactory
            from .scout import TaskDistributor

            start_page, end_page = page_range
            print(f"Поток начинает парсинг {component} со страниц {start_page}-{end_page}")

            all_data = []
            scraper = DNSScraper(proxies)

            page_urls = TaskDistributor.generate_page_urls(base_url, start_page, end_page)

            for page_url in page_urls:
                self.rate_limit()

                try:
                    print(f"Парсинг страницы: {page_url}")
                    data = scraper.scrape_page(page_url)
                    parser = ParserFactory.get_parser(component)
                    result = parser.data_dict_creator(data)

                    if result:
                        all_data.extend(result)

                except Exception as e:
                    print(f"Ошибка при парсинге {page_url}: {e}")
                    continue

            scraper.close()
            print(f"Завершен парсинг {component} ({len(all_data)} товаров)")
            return all_data

        except Exception as e:
            print(f"Ошибка в потоке для {component}: {e}")
            return []

    def scrape_component(self, component: str, base_url: str, proxies: list[str]) -> Dict:
        """Парсинг одного компонента с распределением по страницам"""
        try:
            from .scout import PageScout, TaskDistributor

            print(f"🕵️  Разведка для компонента: {component}")

            total_pages = PageScout().get_total_pages(base_url)
            print(f"📊 Для {component} найдено страниц: {total_pages}")

            page_distributions = TaskDistributor.distribute_pages(total_pages, self.max_workers)
            print(f"📋 Распределение для {component}: {page_distributions}")

            all_component_data = []

            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(page_distributions))) as executor:
                future_to_range = {
                    executor.submit(self.scrape_page_range, component, page_range, base_url, proxies): page_range
                    for page_range in page_distributions
                }

                for future in as_completed(future_to_range):
                    page_range = future_to_range[future]
                    try:
                        page_data = future.result()
                        all_component_data.extend(page_data)
                        print(f"✓ Завершен диапазон {page_range} для {component}")
                    except Exception as e:
                        print(f"✗ Ошибка в диапазоне {page_range}: {e}")

            print(f"✅ Завершен парсинг {component}, собрано {len(all_component_data)} товаров")
            return {
                'component_type': component,
                'data': all_component_data,
                'success': True
            }

        except Exception as e:
            print(f"❌ Критическая ошибка для {component}: {e}")
            return {
                'component_type': component,
                'data': [],
                'success': False,
                'error': str(e)
            }

    def scrape_all(self, components_urls: Dict[str, str], proxies) -> Dict[str, List[Dict]]:
        """Многопоточный парсинг всех компонентов с распределением по страницам"""
        print(f"🚀 Запуск многопоточного парсера для {len(components_urls)} компонентов")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_component = {
                executor.submit(self.scrape_component, component, url, proxies): component
                for component, url in components_urls.items()
            }

            completed = 0
            total = len(components_urls)

            for future in as_completed(future_to_component):
                component = future_to_component[future]
                try:
                    result = future.result()

                    with self.lock:
                        self.results[component] = result['data']

                    completed += 1
                    status = "✓" if result['success'] else "✗"
                    print(f"{status} {component} завершен ({completed}/{total})")

                except Exception as e:
                    print(f"✗ Ошибка при обработке {component}: {e}")
                    completed += 1

        total_products = sum(len(data) for data in self.results.values() if data)
        print(f"🎉 Парсинг завершен! Собрано {total_products} товаров")

        return self.results
