import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import traceback


class NetworkLogger:
    _instance: Optional['NetworkLogger'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        log_dir: str = 'logs',
        log_level: int = logging.DEBUG,
        console_level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5
    ):
        if self._initialized:
            return

        self.log_dir = log_dir
        self.log_level = log_level
        self.console_level = console_level

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('NetworkSimulator')
        self.logger.setLevel(log_level)
        self.logger.handlers = []

        self._setup_file_handler(max_bytes, backup_count)
        self._setup_console_handler()

        self._initialized = True

    def _setup_file_handler(self, max_bytes: int, backup_count: int):
        log_file = os.path.join(
            self.log_dir,
            f"network_{datetime.now().strftime('%Y%m%d')}.log"
        )

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)

        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self._add_context_filter(file_handler)

    def _setup_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)

        console_formatter = logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def _add_context_filter(self, handler):
        class ContextFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'context'):
                    record.context = ''
                if not hasattr(record, 'params'):
                    record.params = ''
                return True

        handler.addFilter(ContextFilter())

    def _format_message(self, message: str, context: dict = None, params: dict = None, include_stack: bool = False):
        parts = [message]

        if params:
            param_str = ' | '.join(f"{k}={v}" for k, v in params.items())
            parts.append(f"[{param_str}]")

        if context:
            context_str = ' | '.join(f"{k}={v}" for k, v in context.items())
            parts.append(f"Context: {context_str}")

        if include_stack:
            stack = ''.join(traceback.format_stack()[-5:-1])
            parts.append(f"\nStack:\n{stack}")

        return ' | '.join(parts)

    def debug(self, message: str, context: dict = None, params: dict = None, include_stack: bool = False):
        formatted = self._format_message(message, context, params, include_stack)
        self.logger.debug(formatted)

    def info(self, message: str, context: dict = None, params: dict = None):
        formatted = self._format_message(message, context, params)
        self.logger.info(formatted)

    def warning(self, message: str, context: dict = None, params: dict = None):
        formatted = self._format_message(message, context, params)
        self.logger.warning(formatted)

    def error(self, message: str, context: dict = None, params: dict = None, include_stack: bool = True):
        formatted = self._format_message(message, context, params, include_stack)
        self.logger.error(formatted)

    def critical(self, message: str, context: dict = None, params: dict = None, include_stack: bool = True):
        formatted = self._format_message(message, context, params, include_stack)
        self.logger.critical(formatted)

    def api_request(self, method: str, endpoint: str, params: dict = None, context: dict = None):
        self.info(
            f"API Request: {method} {endpoint}",
            context=context,
            params=params
        )

    def api_response(self, method: str, endpoint: str, status_code: int, context: dict = None):
        self.info(
            f"API Response: {method} {endpoint} -> {status_code}",
            context=context
        )

    def topology_change(self, change_type: str, details: dict = None, context: dict = None):
        self.info(
            f"Topology Change: {change_type}",
            context=context,
            params=details
        )

    def stp_recalculation(self, root_node: str, link_count: int, context: dict = None):
        self.info(
            "STP Recalculation",
            context=context,
            params={'root_node': root_node, 'link_count': link_count}
        )

    def node_event(self, node_id: str, event: str, context: dict = None):
        self.info(
            f"Node Event: {event}",
            context=context,
            params={'node_id': node_id}
        )

    def link_event(self, link_id: str, event: str, context: dict = None):
        self.info(
            f"Link Event: {event}",
            context=context,
            params={'link_id': link_id}
        )

    def lacp_event(self, link_id: str, event: str, context: dict = None):
        self.debug(
            f"LACP Event: {event}",
            context=context,
            params={'link_id': link_id}
        )

    def bpdu_event(self, node_id: str, event: str, context: dict = None):
        self.debug(
            f"BPDU Event: {event}",
            context=context,
            params={'node_id': node_id}
        )

    def scenario_execution(self, scenario_name: str, result: str, context: dict = None):
        self.info(
            f"Scenario Executed: {scenario_name}",
            context=context,
            params={'result': result}
        )

    def startup(self, component: str, context: dict = None):
        self.info(f"Startup: {component}", context=context)

    def shutdown(self, component: str, context: dict = None):
        self.info(f"Shutdown: {component}", context=context)

    def get_log_file_path(self) -> str:
        return os.path.join(
            self.log_dir,
            f"network_{datetime.now().strftime('%Y%m%d')}.log"
        )


def get_logger(log_dir: str = 'logs', console_level: int = logging.INFO) -> NetworkLogger:
    return NetworkLogger(log_dir=log_dir, console_level=console_level)
