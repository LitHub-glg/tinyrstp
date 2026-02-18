import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class GUILogger:
    _instance: Optional['GUILogger'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        log_dir: str = 'logs',
        log_level: int = logging.DEBUG,
        console_level: int = logging.WARNING,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3
    ):
        if self._initialized:
            return

        self.log_dir = log_dir
        self.log_level = log_level
        self.console_level = console_level

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('NetworkGUI')
        self.logger.setLevel(log_level)
        self.logger.handlers = []

        self._setup_file_handler(max_bytes, backup_count)
        self._setup_console_handler()

        self._initialized = True

    def _setup_file_handler(self, max_bytes: int, backup_count: int):
        log_file = os.path.join(
            self.log_dir,
            f"gui_{datetime.now().strftime('%Y%m%d')}.log"
        )

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)

        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def _setup_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_level)

        console_formatter = logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def api_call(self, method: str, endpoint: str, params: dict = None):
        param_str = f" | params={params}" if params else ""
        self.logger.debug(f"API Call: {method} {endpoint}{param_str}")

    def api_response(self, method: str, endpoint: str, status: str):
        self.logger.debug(f"API Response: {method} {endpoint} -> {status}")

    def user_action(self, action: str, details: dict = None):
        detail_str = f" | {details}" if details else ""
        self.logger.info(f"User Action: {action}{detail_str}")

    def gui_event(self, event: str, details: dict = None):
        detail_str = f" | {details}" if details else ""
        self.logger.debug(f"GUI Event: {event}{detail_str}")

    def get_log_file_path(self) -> str:
        return os.path.join(
            self.log_dir,
            f"gui_{datetime.now().strftime('%Y%m%d')}.log"
        )


def get_gui_logger(log_dir: str = 'logs', console_level: int = logging.WARNING) -> GUILogger:
    return GUILogger(log_dir=log_dir, console_level=console_level)
