from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
from time import sleep
import undetected_chromedriver as uc

from .models import DataParser, ParserResult

class BrowserManager:
    @classmethod
    def start_browser(cls):
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

class DNSScraper:
    def __init__(self):
        self.driver = BrowserManager.start_browser()
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