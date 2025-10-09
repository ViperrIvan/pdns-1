import random
import re
from typing import Any, Dict

def extract_connectors(gpu_string: str) -> str:
    """Извлечение коннекторов из строки видеокарты"""
    connectors = []
    connector_patterns = {
        "DVI": r"DVI[- ]?[ID]?",
        "HDMI": r"HDMI",
        "VGA": r"VGA|D-Sub",
        "DisplayPort": r"DisplayPort|DP"
    }

    for name, pattern in connector_patterns.items():
        if re.search(pattern, gpu_string, re.IGNORECASE):
            connectors.append(name)

    return ", ".join(connectors) if connectors else "N/A"

def clean_price(price_text: str) -> str:
    """Очистка текста цены"""
    return price_text.replace('\u202f', '').replace('P', '').replace('\u2009', '')

def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    """Случайная задержка между запросами"""
    sleep(random.uniform(min_seconds, max_seconds))