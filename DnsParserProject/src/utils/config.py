from dataclasses import dataclass
from typing import Dict


@dataclass
class ScraperConfig:
    max_workers: int = 3
    requests_per_minute: int = 30
    use_threading: bool = True
    save_to_excel: bool = False


class Config:
    URLS = {
        'ram': "https://www.dns-shop.ru/catalog/17a89a3916404e77/operativnaya-pamyat-dimm/",
        'cpu': "https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/",
        'gpu': "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/",
        'cpu_cooler': "https://www.dns-shop.ru/catalog/17a9cc2d16404e77/kulery-dlya-processorov/",
        'motherboard': "https://www.dns-shop.ru/catalog/17a89a0416404e77/materinskie-platy/",
        'cooling_system': "https://www.dns-shop.ru/catalog/17a9cc9816404e77/sistemy-zhidkostnogo-ohlazhdeniya/",
    }

    PROXIES = [0, 1, 2, 3, 4, 5, 6, 7]

    @classmethod
    def get_components(cls):
        return list(cls.URLS.keys())
