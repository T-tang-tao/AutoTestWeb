import logging
from logging.handlers import RotatingFileHandler
import os
# 1. 导入datetime模块，用于生成时间戳
import datetime


class LoggerManager:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger(config)
        return cls._instance

    def _init_logger(self, config: dict = None):
        """
        根据配置设置日志记录器。如果 config 为空，则使用默认配置。

        :param config: 日志配置字典。默认为 None。
        """
        # 默认配置（不变）
        config = config or {
            'level': logging.DEBUG,
            'format': "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s] - %(message)s",
            'console_output': True,
            'log_file':f"logs/app_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log",  # 改为动态生成，由外部传入或默认生成
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        }

        log_level = config.get('level', logging.DEBUG)
        self._logger = logging.getLogger()
        self._logger.setLevel(log_level)

        # 日志格式（不变）
        formatter = logging.Formatter(config['format'])

        # 清除现有Handler（防止重复输出）
        if self._logger.handlers:
            for handler in self._logger.handlers[:]:
                self._logger.removeHandler(handler)

        # 控制台输出（不变）
        if config.get('console_output', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # 文件输出（核心：使用外部传入的带时间戳的log_file）
        log_file = config.get('log_file')
        if log_file:
            # 确保日志目录存在（不变）
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # 日志轮转配置（不变）
            file_handler = RotatingFileHandler(
                log_file,
                encoding='utf-8',
                maxBytes=config.get('max_bytes', 10 * 1024 * 1024),
                backupCount=config.get('backup_count', 5)
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        self._logger.debug('日志配置加载完成，日志文件：%s', log_file)

    @classmethod
    def configure(cls, config: dict):
        """Apply an explicit logging configuration to the shared logger."""
        if cls._instance is None:
            cls(config=config)
        else:
            cls._instance._init_logger(config)
        return cls._instance

    def get_logger(self):
        return self._logger


# 2. 示例用法：动态生成带时间戳的日志文件名
if __name__ == "__main__":
    # 初始化日志管理器并记录日志
    logger_manager = LoggerManager()
    logger = logger_manager.get_logger()
    logger.debug('调试日志：带时间戳的日志文件已创建')
    logger.info('信息日志：这是一条测试信息')
    logger.warning('警告日志：这是一条测试警告')
