from .core.parser import DNSScraper, ParserFactory, BrowserManager
from .core.thread_manager import AdvancedThreadedScraper
from .core.scout import PageScout, TaskDistributor
from .core.models import (
    DataParser, RamDataParser, MotherboardDataParser, CpuCoolerDataParser,
    CoolingSystemDataParser, CpuDataParser, GpuDataParser, ComponentScorer
)
from .storage.saver import ExcelDataSaver, SQLDataSaver
from .utils.config import Config, ScraperConfig
from .utils.logger import setup_logger

__version__ = "2.0.0"
__all__ = [
    'DNSScraper', 'ParserFactory', 'BrowserManager',
    'AdvancedThreadedScraper', 'PageScout', 'TaskDistributor',
    'DataParser', 'RamDataParser', 'MotherboardDataParser', 'CpuCoolerDataParser',
    'CoolingSystemDataParser', 'CpuDataParser', 'GpuDataParser', 'ComponentScorer',
    'ExcelDataSaver', 'SQLDataSaver',
    'Config', 'ScraperConfig', 'setup_logger'
]