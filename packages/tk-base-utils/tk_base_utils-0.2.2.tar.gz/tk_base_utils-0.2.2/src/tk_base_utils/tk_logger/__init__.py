"""temp3 - 基于logging的日志程序

提供全局唯一的logger和装饰器方式的日志记录功能。
"""

from .logger import get_logger, reload_logger,reset_logger
from .decorators import logger_wrapper
from .config import set_config_path

__version__ = "0.1.1"
__all__ = ["get_logger", "reload_logger","reset_logger", "logger_wrapper", "set_config_path"]
