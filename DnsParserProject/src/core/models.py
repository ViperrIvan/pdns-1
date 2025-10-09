from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
import re


class DataParser:
    @classmethod
    @abstractmethod
    def data_dict_creator(cls, component_info):
        pass

class RamDataParser(DataParser):
    @classmethod
    def data_dict_creator(cls, component_info):
        ram_string = component_info[0]
        price = component_info[1]
        href = component_info[2]
        # Дополнительные поиски для параметров
        capacity_match = re.search(r'([\d.]+)\s*Г?Б', ram_string, re.IGNORECASE)
        type_match = re.search(r'(DDR\d+)', ram_string, re.IGNORECASE)
        speed_match = re.search(r'([\d.]+)\s*М?Гц', ram_string, re.IGNORECASE)
        timings_match = re.search(r'(\d+)\(CL\)[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)', ram_string) or \
                        re.search(r'CL(\d+)[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)', ram_string) or \
                        re.search(r'(\d+)[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)', ram_string)
        modules_match = re.search(r'([\d.]+)\s*Г?Б?x?\s*([\d.]+)\s*шт', ram_string, re.IGNORECASE)

        try:
            # Формируем строку таймингов
            if timings_match:
                if ram_string.count('(CL)') > 0:
                    # Формат с (CL): 11(CL)-11-11-28
                    timings_str = f"{timings_match.group(1)}-{timings_match.group(2)}-{timings_match.group(3)}-{timings_match.group(4)}"
                    cl = timings_match.group(1)
                elif 'CL' in ram_string:
                    # Формат с CL: CL11-11-11-28
                    timings_str = f"{timings_match.group(1)}-{timings_match.group(2)}-{timings_match.group(3)}-{timings_match.group(4)}"
                    cl = timings_match.group(1)
                else:
                    # Простой формат: 11-11-11-28
                    timings_str = f"{timings_match.group(1)}-{timings_match.group(2)}-{timings_match.group(3)}-{timings_match.group(4)}"
                    cl = timings_match.group(1)
            else:
                timings_str = "N/A"
                cl = "N/A"

            result = {
                "Название": re.match(r'^(.*?)(?:\s*\[|$)', ram_string).group(1).strip(),
                "Цена": price,
                "Ссылка": href,
                "Общий объем (ГБ)": float(capacity_match.group(1).replace(',', '.')) if capacity_match else "N/A",
                "Тип памяти": type_match.group(1).upper() if type_match else "N/A",
                "Размер модуля (ГБ)": float(modules_match.group(1).replace(',', '.')) if modules_match else "N/A",
                "Количество модулей": int(modules_match.group(2)) if modules_match else "N/A",
                "Частота (МГц)": int(float(speed_match.group(1).replace(',', '.'))) if speed_match else "N/A",
                "Тайминги": timings_str,
                "Латентность (CL)": cl
            }
            return result
        except (ValueError, AttributeError, IndexError) as e:
            print(f"Ошибка обработки данных: {e} в строке: {ram_string}")
            return None

class MotherboardDataParser(DataParser):
    @classmethod
    def data_dict_creator(cls, component_info):
        mb_string = component_info[0]
        price = component_info[1]
        href = component_info[2]
        # Основные параметры для поиска
        socket_match = re.search(r'(LGA\s\d+|BGA\d+|Socket\s*\d+|s?\d+)', mb_string, re.IGNORECASE)
        chipset_match = re.search(r'(Intel|AMD)\s*([A-Z0-9]+)', mb_string, re.IGNORECASE)
        ram_slots_match = re.search(r'(\d+)x(DDR\d[L]?)[-\s]*(\d+)?\s*МГц', mb_string, re.IGNORECASE)
        form_factor_match = re.search(r'(Micro-ATX|Mini-ITX|Mini-DTX|ATX|E-ATX|XL-ATX|Thin Mini-ITX)', mb_string,
                                      re.IGNORECASE)
        pcie_match = re.search(r'(\d+)xPCI-Ex(\d+)', mb_string, re.IGNORECASE)
        cpu_support_match = re.search(r'(Intel|AMD)\s*(.*?)\s*\(', mb_string)

        try:
            result = {
                "Название": re.match(r'^(.*?)(?:\s*\[|$)', mb_string).group(1).strip(),
                "Цена": price,
                "Ссылка": href,
                "Сокет": socket_match.group() if socket_match else "N/A",
                "Чипсет": f"{chipset_match.group(1)} {chipset_match.group(2)}" if chipset_match else "N/A",
                "Количество слотов памяти": int(ram_slots_match.group(1)) if ram_slots_match else "N/A",
                "Тип слотов памяти": ram_slots_match.group(2).upper() if ram_slots_match else "N/A",
                "Частота слотов памяти": f"{ram_slots_match.group(3)} МГц" if ram_slots_match and ram_slots_match.group(
                    3) else "N/A",
                "Форм-фактор": form_factor_match.group() if form_factor_match else "Нестандартный",
                "Количество слотов PCI-E": int(pcie_match.group(1)) if pcie_match else "N/A",
                "Версия слотов PCI-E": f"x{pcie_match.group(2)}" if pcie_match else "N/A",
                "Поддержка CPU": cpu_support_match.group().strip() if cpu_support_match else "N/A"
            }

            # Дополнительно проверяем поддержку CPU в другом формате
            if result["Поддержка CPU"] == "N/A":
                cpu_alt_match = re.search(r'\b(?:Intel|AMD)\b.*?(?:Celeron|Core|Ryzen|Athlon)\s*\w*', mb_string,
                                          re.IGNORECASE)
                if cpu_alt_match:
                    result["Поддержка CPU"] = cpu_alt_match.group().strip()

            return result
        except (ValueError, AttributeError, IndexError) as e:
            print(f"Ошибка обработки данных: {e} в строке: {mb_string}")
            return None

class CpuCoolerDataParser(DataParser):
    @classmethod
    def data_dict_creator(cls, component_info):
        cooler_string = component_info[0]
        price = component_info[1]
        href = component_info[2]
        # Основные параметры для поиска
        base_match = re.search(r'основание\s*-\s*([а-яА-Яa-zA-Z]+)', cooler_string, re.IGNORECASE)
        rpm_match = re.search(r'(\d+)\s*об/\s*мин', cooler_string)
        noise_match = re.search(r'(\d+\.?\d*)\s*дБ', cooler_string)
        pin_match = re.search(r'(\d+)\s*pin', cooler_string, re.IGNORECASE)
        tdp_match = re.search(r'(\d+)\s*Вт', cooler_string)
        fan_size_match = re.search(r'(\d+)\s*мм', cooler_string)

        try:
            result = {
                "Название": re.match(r'^(.*?)(?:\s*\[|$)', cooler_string).group(1).strip(),
                "Цена": price,
                "Ссылка": href,
                "Материал основания": base_match.group(1).capitalize() if base_match else "N/A",
                "Скорость вращения": f"{rpm_match.group(1)} об/мин" if rpm_match else "N/A",
                "Уровень шума": f"{noise_match.group(1)} дБ" if noise_match else "N/A",
                "Разъем питания": f"{pin_match.group(1)} pin" if pin_match else "N/A",
                "Макс. TDP": f"{tdp_match.group(1)} Вт" if tdp_match else "N/A",
                "Размер вентилятора": f"{fan_size_match.group(1)} мм" if fan_size_match else "N/A"
            }

            # Дополнительно проверяем размер вентилятора по названию (например, R94 может означать 94мм)
            if result["Размер вентилятора"] == "N/A":
                size_from_name = re.search(r'(\d{2,3})(?:mm|мм|\s*мм)?', result["Название"])
                if size_from_name:
                    result["Размер вентилятора"] = f"{size_from_name.group(1)} мм"

            return result
        except (ValueError, AttributeError, IndexError) as e:
            print(f"Ошибка обработки данных: {e} в строке: {cooler_string}")
            return None


class CoolingSystemDataParser(DataParser):
    @classmethod
    def data_dict_creator(cls, component_info):
        cooling_string = component_info[0]
        price = component_info[1]
        href = component_info[2]
        # Основные параметры для поиска
        fan_size_match = re.search(r'(\d+)\s*мм', cooling_string)
        sections_match = re.search(r'(\d+)\s*секци[ияей]', cooling_string)
        power_match = re.search(r'(SATA Power|3 pin|4 pin|15 pin)', cooling_string, re.IGNORECASE)
        radiator_match = re.search(r'радиатор\s*-\s*([а-яА-Яa-zA-Z]+)', cooling_string, re.IGNORECASE)
        tdp_match = re.search(r'TDP\s*(\d+)\s*Вт', cooling_string, re.IGNORECASE)
        fan_count_match = re.search(r'(\d+)\s*вентилятор', cooling_string)
        try:
            result = {
                "Название": re.match(r'^(.*?)(?:\s*\[|$)', cooling_string).group(1).strip(),
                "Цена": price,
                "Ссылка": href,
                "Размер вентилятора(ов)": f"{fan_size_match.group(1)} мм" if fan_size_match else "N/A",
                "Количество секций": sections_match.group(1) if sections_match else "1",  # По умолчанию 1 секция
                "Количество вентиляторов": fan_count_match.group(1) if fan_count_match else
                sections_match.group(1) if sections_match else "1",  # Обычно равно количеству секций
                "Питание": power_match.group(1) if power_match else "N/A",
                "Материал радиатора": radiator_match.group(1).capitalize() if radiator_match else "N/A",
                "TDP": f"{tdp_match.group(1)} Вт" if tdp_match else "N/A"
            }

            # Автоматическое определение типа охлаждения по названию
            if result["Тип охлаждения"] == "N/A":
                if any(word in cooling_string.lower() for word in ['liquid', 'water', 'сжо', 'жидкост']):
                    result["Тип охлаждения"] = "Жидкостное"
                else:
                    result["Тип охлаждения"] = "Воздушное"

            # Уточнение количества вентиляторов для СЖО
            if result["Тип охлаждения"] == "Жидкостное":
                if "360" in result["Название"]:
                    result["Количество вентиляторов"] = "3"
                elif "240" in result["Название"]:
                    result["Количество вентиляторов"] = "2"
                elif "120" in result["Название"]:
                    result["Количество вентиляторов"] = "1"

            return result
        except (ValueError, AttributeError, IndexError) as e:
            print(f"Ошибка обработки данных: {e} в строке: {cooling_string}")
            return None

class CpuDataParser(DataParser):
    @classmethod
    def data_dict_creator(cls, component_info):
        cpu_string = component_info[0]
        price = component_info[1]
        href = component_info[2]
        # Универсальный шаблон для всех типов процессоров
        pattern = r"""
            ^(.*?)\s*                # Название процессора
            (?:\[.*?)?               # Опциональное начало характеристик
            (LGA\s\d+|AM\d|FM\d\+?|Socket\s*\d+),?\s*  # Сокет (LGA 1200, AM4, FM2+, Socket AM4)
            (?:.*?)?                 # Пропускаем возможные дополнительные символы
            (\d+)\s*(?:ядер[а]?|x|х)\s*  # Количество ядер
            (?:.*?)?                 # Пропускаем возможные дополнительные символы
            ([\d.]+)\s*ГГц,?\s*      # Частота
            (?:L2\s*[-—]?\s*([\d.]+)\s*МБ,?\s*)?  # Опциональный L2
            (?:L3\s*[-—]?\s*([\d.]+)\s*МБ,?\s*)?  # Опциональный L3
            (?:.*?)?                 # Пропускаем возможные дополнительные характеристики
            (\d+)\s*(?:x|х|канал[а]?|каналов)\s*(?:DDR\d[L]?)\s*,?\s*  # Память
            (?:.*?)?                 # Пропускаем возможные дополнительные символы
            (?:([^,]+?),?\s*)?       # Графика (опционально)
            (?:.*?)?                 # Пропускаем возможные дополнительные символы
            TDP\s*[-—]?\s*([\d.]+)\s*Вт  # TDP
            .*?$                    # Конец строки
        """

        match = re.search(pattern, cpu_string, re.VERBOSE | re.IGNORECASE)
        if not match:
            print(f"Не удалось распарсить строку: {cpu_string}")
            return None

        try:
            return {
                "Название": match.group(1).strip(),
                "Цена": price,
                "Ссылка": href,
                "Сокет": match.group(2).strip(),
                "Количество ядер": int(match.group(3)),
                "Частота (ГГц)": float(match.group(4).replace(',', '.')),
                "Кэш L2 (МБ)": float(match.group(5).replace(',', '.')) if match.group(5) else "N/A",
                "Кэш L3 (МБ)": float(match.group(6).replace(',', '.')) if match.group(6) else "N/A",
                "Количество каналов памяти": int(match.group(7)),
                "Графика": match.group(8).strip() if match.group(8) else "Нет",
                "TDP (Вт)": int(float(match.group(9).replace(',', '.')))
            }
        except (ValueError, IndexError, AttributeError) as e:
            print(f"Ошибка обработки данных: {e} в строке: {cpu_string}")
            return None

class GpuDataParser(DataParser):
    @classmethod
    def data_dict_creator(cls, component_info):
        def extract_connectors(gpu_string):
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

        gpu_string = component_info[0]
        price = component_info[1]
        href = component_info[2]

        # Дополнительные поиски для параметров, которые могут быть в разных местах
        memory_bus_match = re.search(r'([\d.]+)\s*бит', gpu_string)
        memory_type_match = re.search(r'(DDR\d|GDDR\d)', gpu_string, re.IGNORECASE)
        memory_size_match = re.search(r'([\d.]+)\s*Г?Б', gpu_string, re.IGNORECASE)
        gpu_clock_match = re.search(r'(?:GPU\s*:?\s*)?([\d.]+)\s*М?Гц', gpu_string, re.IGNORECASE)
        memory_clock_match = re.search(r'(?:память\s*:?\s*)?([\d.]+)\s*М?Гц', gpu_string, re.IGNORECASE)
        pcie_match = re.search(r'PCI[Ee]\s*([\d.]+)', gpu_string, re.IGNORECASE)

        try:
            result = {
                "Название": re.match(r'^(.*?)(?:\s*\[|$)', gpu_string).group(1).strip(),
                "Цена": price,
                "Ссылка": href,
                "Объем памяти (ГБ)": float(
                    memory_size_match.group(1).replace(',', '.')) if memory_size_match else "N/A",
                "Тип памяти": memory_type_match.group().upper() if memory_type_match else "N/A",
                "Шина памяти (бит)": int(memory_bus_match.group(1)) if memory_bus_match else "N/A",
                "Частота GPU (МГц)": int(
                    float(gpu_clock_match.group(1).replace(',', '.'))) if gpu_clock_match else "N/A",
                "Частота памяти (МГц)": int(
                    float(memory_clock_match.group(1).replace(',', '.'))) if memory_clock_match else "N/A",
                "Версия PCIe": pcie_match.group(1) if pcie_match else "N/A",
                "Разъемы": extract_connectors(gpu_string)
            }
            return result
        except (ValueError, AttributeError, IndexError) as e:
            print(f"Ошибка обработки данных: {e} в строке: {gpu_string}")
            return None


@dataclass
class ParserResult:
    component_type: str
    data: list
    success: bool = True
    error: Optional[str] = None


class ComponentScorer:
    def __init__(self):
        self.weights = {
            'cpu': {
                'Количество ядер': 0.25,
                'Частота (ГГц)': 0.20,
                'Кэш L2 (МБ)': 0.15,
                'Кэш L3 (МБ)': 0.15,
                'Количество каналов памяти': 0.10,
                'Графика': 0.05,
                'TDP (Вт)': 0.10
            },
            'ram': {
                'Общий объем (ГБ)': 0.30,
                'Тип памяти': 0.20,
                'Размер модуля (ГБ)': 0.10,
                'Количество модулей': 0.10,
                'Частота (МГц)': 0.15,
                'Тайминги': 0.10,
                'Латентность (CL)': 0.05
            },
            'motherboard': {
                'Чипсет': 0.25,
                'Количество слотов памяти': 0.15,
                'Тип слотов памяти': 0.15,
                'Частота слотов памяти': 0.15,
                'Форм-фактор': 0.10,
                'Количество слотов PCI-E': 0.10,
                'Поддержка CPU': 0.10
            },
            'air_cooler': {
                'Материал основания': 0.20,
                'Скорость вращения': 0.25,
                'Уровень шума': 0.20,
                'Разъем питания': 0.10,
                'Макс. TDP': 0.15,
                'Размер вентилятора': 0.10
            },
            'water_cooling': {
                'Размер вентилятора(ов)': 0.20,
                'Количество секций': 0.25,
                'Количество вентиляторов': 0.20,
                'Питание': 0.15,
                'TDP': 0.20
            },
            'gpu': {
                'Объем памяти (ГБ)': 0.25,
                'Тип памяти': 0.20,
                'Шина памяти (бит)': 0.20,
                'Частота GPU (МГц)': 0.15,
                'Версия PCIe': 0.10,
                'Разъемы': 0.10
            }
        }

    def score_cpu(self, specs):
        """Оценка процессора"""
        score = 0

        # Количество ядер (0-100 баллов)
        cores_score = min(specs['Количество ядер'] * 10, 100) if specs['Количество ядер'] <= 16 else 100
        score += cores_score * self.weights['cpu']['Количество ядер']

        # Частота (0-100 баллов)
        freq_score = min((specs['Частота (ГГц)'] * 1000 - 2000) / 20, 100) if specs['Частота (ГГц)'] * 1000 <= 5000 else 100
        score += freq_score * self.weights['cpu']['Частота (ГГц)']

        # Кэш L2 (0-100 баллов)
        l2_score = min(specs['Кэш L2 (МБ)'] * 5, 100)
        score += l2_score * self.weights['cpu']['Кэш L2 (МБ)']

        # Кэш L3 (0-100 баллов)
        l3_score = min(specs['Кэш L3 (МБ)'] * 2, 100)
        score += l3_score * self.weights['cpu']['Кэш L3 (МБ)']

        # Количество каналов памяти
        channels_score = {1: 30, 2: 70, 4: 100, 8: 100}.get(specs['Количество каналов памяти'], 0)
        score += channels_score * self.weights['cpu']['Количество каналов памяти']

        # Графика
        graphics_score = 100 if specs['Графика'] != 'Нет' else 0
        score += graphics_score * self.weights['cpu']['Графика']

        # TDP (чем меньше - тем лучше)
        tdp_score = max(0, 100 - (specs['TDP (Вт)'] / 2))
        score += tdp_score * self.weights['cpu']['TDP (Вт)']

        return round(score, 2)

    def score_ram(self, specs):
        """Оценка оперативной памяти"""
        score = 0

        # Общий объем (GB)
        total_size_score = min(specs['Общий объем (ГБ)'] * 2, 100)
        score += total_size_score * self.weights['ram']['Общий объем (ГБ)']

        # Тип памяти
        memory_type_scores = {'DDR3': 30, 'DDR4': 70, 'DDR5': 100}
        memory_type_score = memory_type_scores.get(specs['Тип памяти'], 0)
        score += memory_type_score * self.weights['ram']['Тип памяти']

        # Размер модуля
        module_size_score = min(specs['Размер модуля (ГБ)'] * 5, 100)
        score += module_size_score * self.weights['ram']['Размер модуля (ГБ)']

        # Количество модулей
        modules_score = min(specs['Количество модулей'] * 25, 100)
        score += modules_score * self.weights['ram']['Количество модулей']

        # Частота
        freq_scores = {2133: 30, 2666: 40, 3200: 60, 3600: 70, 4000: 80, 4800: 90, 5600: 100}
        freq_score = max(freq_scores.get(specs['Частота (МГц)'], 0),
                         min(specs['Частота (МГц)'] / 40, 100))
        score += freq_score * self.weights['ram']['Частота (МГц)']

        # Тайминги (чем меньше - тем лучше)
        # Извлекаем числовое значение из строки таймингов
        timings_value = float(specs['Тайминги'].split('-')[0]) if isinstance(specs['Тайминги'], str) and '-' in specs['Тайминги'] else specs['Тайминги']
        timings_score = max(0, 100 - (timings_value * 5))
        score += timings_score * self.weights['ram']['Тайминги']

        # Латентность
        latency_score = max(0, 100 - (specs['Латентность (CL)'] * 10))
        score += latency_score * self.weights['ram']['Латентность (CL)']

        return round(score, 2)

    def score_motherboard(self, specs):
        """Оценка материнской платы"""
        score = 0

        # Чипсет (примерные оценки)
        chipset_scores = {
            'H610': 40, 'B660': 60, 'H670': 70, 'Z690': 85, 'Z790': 95,
            'A520': 40, 'B550': 65, 'X570': 85, 'X670': 95
        }
        chipset_score = chipset_scores.get(specs['Чипсет'], 50)
        score += chipset_score * self.weights['motherboard']['Чипсет']

        # Количество слотов памяти
        slots_score = min(specs['Количество слотов памяти'] * 25, 100)
        score += slots_score * self.weights['motherboard']['Количество слотов памяти']

        # Тип слотов памяти
        memory_type_score = 100 if specs['Тип слотов памяти'] in ['DDR4', 'DDR5'] else 50
        score += memory_type_score * self.weights['motherboard']['Тип слотов памяти']

        # Частота слотов памяти (извлекаем числовое значение)
        mem_freq_value = int(specs['Частота слотов памяти'].split()[0]) if isinstance(specs['Частота слотов памяти'], str) else specs['Частота слотов памяти']
        mem_freq_score = min(mem_freq_value / 40, 100)
        score += mem_freq_score * self.weights['motherboard']['Частота слотов памяти']

        # Форм-фактор
        form_factor_scores = {'Mini-ITX': 60, 'Micro-ATX': 70, 'ATX': 85, 'E-ATX': 95}
        form_factor_score = form_factor_scores.get(specs['Форм-фактор'], 50)
        score += form_factor_score * self.weights['motherboard']['Форм-фактор']

        # Количество слотов PCI-E
        pcie_score = min(specs['Количество слотов PCI-E'] * 20, 100)
        score += pcie_score * self.weights['motherboard']['Количество слотов PCI-E']

        # Совместимость с CPU
        brand_score = 100 if any(brand in specs['Поддержка CPU'].lower() for brand in ['intel', 'amd']) else 0
        score += brand_score * self.weights['motherboard']['Поддержка CPU']

        return round(score, 2)

    def score_air_cooler(self, specs):
        """Оценка воздушного охлаждения"""
        score = 0

        # Материал основания
        material_scores = {'aluminum': 60, 'copper': 85, 'copper+heatpipes': 100}
        material_score = material_scores.get(specs['Материал основания'].lower(), 50)
        score += material_score * self.weights['air_cooler']['Материал основания']

        # Скорость вращения (извлекаем числовое значение)
        speed_value = int(specs['Скорость вращения'].split()[0]) if isinstance(specs['Скорость вращения'], str) else specs['Скорость вращения']
        speed_score = min(speed_value / 20, 100)
        score += speed_score * self.weights['air_cooler']['Скорость вращения']

        # Уровень шума (извлекаем числовое значение)
        noise_value = float(specs['Уровень шума'].split()[0]) if isinstance(specs['Уровень шума'], str) else specs['Уровень шума']
        noise_score = max(0, 100 - (noise_value * 5))
        score += noise_score * self.weights['air_cooler']['Уровень шума']

        # Разъем питания
        connector_scores = {'3pin': 60, '4pin': 85, 'PWM': 100}
        # Извлекаем только цифры из строки
        pin_value = ''.join(filter(str.isdigit, specs['Разъем питания'])) if isinstance(specs['Разъем питания'], str) else str(specs['Разъем питания'])
        connector_score = connector_scores.get(pin_value, 50)
        score += connector_score * self.weights['air_cooler']['Разъем питания']

        # Макс TDP (извлекаем числовое значение)
        tdp_value = int(specs['Макс. TDP'].split()[0]) if isinstance(specs['Макс. TDP'], str) else specs['Макс. TDP']
        tdp_score = min(tdp_value / 2, 100)
        score += tdp_score * self.weights['air_cooler']['Макс. TDP']

        # Размер вентилятора (извлекаем числовое значение)
        size_value = int(specs['Размер вентилятора'].split()[0]) if isinstance(specs['Размер вентилятора'], str) else specs['Размер вентилятора']
        size_score = min(size_value / 2, 100)
        score += size_score * self.weights['air_cooler']['Размер вентилятора']

        return round(score, 2)

    def score_water_cooling(self, specs):
        """Оценка водяного охлаждения"""
        score = 0

        # Размер вентилятора (извлекаем числовое значение)
        fan_size_value = int(specs['Размер вентилятора(ов)'].split()[0]) if isinstance(specs['Размер вентилятора(ов)'], str) else specs['Размер вентилятора(ов)']
        fan_size_score = min(fan_size_value / 2, 100)
        score += fan_size_score * self.weights['water_cooling']['Размер вентилятора(ов)']

        # Количество секций радиатора
        sections_score = min(int(specs['Количество секций']) * 20, 100)
        score += sections_score * self.weights['water_cooling']['Количество секций']

        # Количество вентиляторов
        fans_score = min(int(specs['Количество вентиляторов']) * 25, 100)
        score += fans_score * self.weights['water_cooling']['Количество вентиляторов']

        # Питание
        power_scores = {'3pin': 60, '4pin': 85, 'PWM': 100, 'SATA': 70, 'MOLEX': 50}
        power_score = power_scores.get(specs['Питание'], 50)
        score += power_score * self.weights['water_cooling']['Питание']

        # TDP (извлекаем числовое значение)
        tdp_value = int(specs['TDP'].split()[0]) if isinstance(specs['TDP'], str) else specs['TDP']
        tdp_score = min(tdp_value / 2, 100)
        score += tdp_score * self.weights['water_cooling']['TDP']

        return round(score, 2)

    def score_gpu(self, specs):
        """Оценка видеокарты"""
        score = 0

        # Объем памяти (GB)
        memory_score = min(specs['Объем памяти (ГБ)'] * 5, 100)
        score += memory_score * self.weights['gpu']['Объем памяти (ГБ)']

        # Тип памяти
        memory_type_scores = {'GDDR5': 40, 'GDDR6': 70, 'GDDR6X': 85, 'HBM2': 95}
        memory_type_score = memory_type_scores.get(specs['Тип памяти'], 50)
        score += memory_type_score * self.weights['gpu']['Тип памяти']

        # Шина памяти (bit)
        bus_score = min(specs['Шина памяти (бит)'] * 1.5, 100)
        score += bus_score * self.weights['gpu']['Шина памяти (бит)']

        # Частота GPU (MHz)
        freq_score = min(specs['Частота GPU (МГц)'] / 20, 100)
        score += freq_score * self.weights['gpu']['Частота GPU (МГц)']

        # Версия PCI-E
        pcie_scores = {'3.0': 60, '4.0': 85, '5.0': 100}
        pcie_score = pcie_scores.get(specs['Версия PCIe'], 50)
        score += pcie_score * self.weights['gpu']['Версия PCIe']

        # Разъемы (количество)
        connectors_score = min(len(specs['Разъемы'].split(',')) * 20, 100) if isinstance(specs['Разъемы'], str) else 50
        score += connectors_score * self.weights['gpu']['Разъемы']

        return round(score, 2)

    def evaluate_system(self, components):
        """Оценка всей системы"""
        scores = {}

        if 'cpu' in components:
            scores['cpu'] = self.score_cpu(components['cpu'])

        if 'ram' in components:
            scores['ram'] = self.score_ram(components['ram'])

        if 'motherboard' in components:
            scores['motherboard'] = self.score_motherboard(components['motherboard'])

        if 'air_cooler' in components:
            scores['air_cooler'] = self.score_air_cooler(components['air_cooler'])

        if 'water_cooling' in components:
            scores['water_cooling'] = self.score_water_cooling(components['water_cooling'])

        if 'gpu' in components:
            scores['gpu'] = self.score_gpu(components['gpu'])

        # Общая оценка системы (средневзвешенная)
        total_score = sum(scores.values()) / len(scores) if scores else 0

        return {
            'component_scores': scores,
            'total_score': round(total_score, 2),
            'rating': self._get_rating(total_score)
        }

    def _get_rating(self, score):
        """Получить текстовую оценку"""
        if score >= 90:
            return "Отлично (A)"
        elif score >= 80:
            return "Очень хорошо (B)"
        elif score >= 70:
            return "Хорошо (C)"
        elif score >= 60:
            return "Удовлетворительно (D)"
        else:
            return "Плохо (F)"