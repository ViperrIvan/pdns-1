import logging

import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
from time import sleep
import undetected_chromedriver as uc
import time
import requests

from .models import RamDataParser, CpuCoolerDataParser, CoolingSystemDataParser, CpuDataParser, GpuDataParser, MotherboardDataParser

class BrowserManager:
    @classmethod
    def start_browser(cls, proxies):
        # 1. Расширенные настройки Chrome
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--guest')  # Критически важный параметр
        options.add_argument('--no-first-run')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-geolocation')

        is_proxy_used = False
        for proxy in proxies:
            if cls.check_proxy_simple(proxy):
                options.add_argument(f"--proxy-server={proxy}")
                is_proxy_used = True

        if not is_proxy_used:
            print("Все прокси не доступны")
            logging.error("❌ Не удается установить соединение ни с одним прокси")
            logging.info("Завершение работы парсера...")
            sys.exit()


        # 2. Ротация User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Vivaldi/6.2.3105.58'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        # 3. Запуск браузера с улучшенной маскировкой
        driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=True,
            version_main=140,
        )

        # 4. Кастомные заголовки
        # Правильный формат для CDP команды
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
            'headers': {
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Sec-CH-UA': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"Windows"',
                'Referer': 'https://www.dns-shop.ru/',
                'DNT': '1'
            }
        })

        return driver

    @staticmethod
    # Эмулируем человеческое поведение
    def human_like_actions(next_page, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.2);")
        sleep(random.uniform(0.5, 1.5))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
        sleep(random.uniform(0.7, 2))
        next_page_elem = driver.find_element(By.XPATH, next_page)
        driver.execute_script("arguments[0].scrollIntoView(true);", next_page_elem)
        sleep(random.uniform(1, 3))

    @classmethod
    def check_proxy_simple(cls, proxy, timeout=10):
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }

        try:
            start_time = time.time()
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=timeout
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                logging.info(1, f"✅ Прокси {proxy} доступен")
                logging.info(1, f"⏱️  Время ответа: {response_time:.2f} сек")
                logging.info(1, f"🌐 IP адрес: {response.json()['origin']}")
                return True
            else:
                logging.error(f"❌ Прокси недоступен, статус: {response.status_code}")
                return False

        except requests.exceptions.ConnectTimeout:
            logging.warn(f"⏰ Таймаут подключения к прокси {proxy}")
            return False
        except requests.exceptions.ConnectionError:
            logging.error(f"🔌 Ошибка подключения к прокси {proxy}")
            return False
        except Exception as e:
            logging.error(f"❌ Ошибка при проверке прокси: {e}")
            return False

class DNSScraper:
    def __init__(self, proxies):
        self.driver = BrowserManager.start_browser(proxies)
        self.xpathes = {
            "name": "//div[@class='catalog-product__name-wrapper']//span",
            "price": "//div[@class='product-buy__price']",
            "href": "//a[@class='catalog-product__name ui-link ui-link_black']",
            "next-page": "//button[contains(text(), 'Показать ещё')]"
        }

    def scrape_page(self, url):
        # Получение страницы
        self.driver.get(url)
        sleep(random.uniform(5, 10))

        # Ожидаем загрузки элементов
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, self.xpathes['name'])))

        while self.driver.find_element(By.XPATH, self.xpathes["next-page"]):
            BrowserManager.human_like_actions(self.xpathes["next-page"], self.driver)  # Имитируем поведение человека
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, self.xpathes["next-page"]))
            )
            button.click()
            sleep(random.uniform(0.5, 1.5))

        # Получаем элементы с обработкой ошибок
        names = self.__find_names()
        prices = self.__find_prices()
        hrefs = self.__find_hrefs()

        return [names, prices, hrefs]

    def __find_names(self):
        # Поиск имен
        return [name.text for name in self.driver.find_elements(By.XPATH, self.xpathes['name'])]

    def __find_prices(self):
        # Поиск и обработка цен
        return [price.text.replace('\u202f', '').replace('P', '').replace('\u2009', '') for price in self.driver.find_elements(By.XPATH, self.xpathes['price'])]

    def __find_hrefs(self):
        return [href.get_attribute('href') for href in self.driver.find_elements(By.XPATH, self.xpathes['href'])]

    def close(self):
        self.driver.quit()

class ParserFactory:
    @staticmethod
    def get_parser(component_type):
        parsers = {
            'ram': RamDataParser,
            'cpu': CpuDataParser,
            'gpu': GpuDataParser,
            'cpu_cooler': CpuCoolerDataParser,
            'motherboard': MotherboardDataParser,
            'cooling_system': CoolingSystemDataParser
        }
        return parsers.get(component_type.lower())
