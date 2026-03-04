"""
Logging utilities module.
Configures colored console output and concurrent-safe rotating file logging.
The global logger instance `logs` can be imported directly.
"""
import logging
import os
import time

import colorlog
from concurrent_log_handler import ConcurrentRotatingFileHandler

from utils.settings import FILE_PATH

logs_path = FILE_PATH['log']
if not os.path.exists(logs_path):
    os.mkdir(logs_path)

logfile_name = os.path.join(logs_path, 'test{}.log'.format(time.strftime('%Y%m%d-%H%M')))


class HandleLogs:

    @classmethod
    def setting_log_color(cls):
        """Configure the console log color scheme."""
        log_color_config = {
            'NOTSET': 'white',
            'FATAL': 'scarlet',
            'DEBUG': 'cyan',
            'INFO': 'green',
            'ERROR': 'red',
            'WARNING': 'yellow',
            'CRITICAL': 'blue',
        }
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s [%(asctime)s-%(filename)s:%(lineno)d-%(module)s:%(funcName)s]: %(message)s',
            log_colors=log_color_config,
        )
        return formatter

    @classmethod
    def output_logs(cls, log_level="debug"):
        """Create a logger instance that outputs to both console (colored) and file (concurrent-safe)."""
        _nameToLevel = {
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.FATAL,
            'ERROR': logging.ERROR,
            'WARN': logging.WARNING,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'NOTSET': logging.NOTSET,
        }
        log_level = _nameToLevel.get(log_level.upper())
        logger = logging.getLogger(__name__)
        color_formate = cls.setting_log_color()
        logger.setLevel(log_level)

        if not logger.handlers:
            log_format = logging.Formatter(
                '%(levelname)s [%(asctime)s%(filename)s:%(funcName)s:%(lineno)d]: %(message)s',
            )
            sh = logging.StreamHandler()
            sh.setFormatter(color_formate)
            logger.addHandler(sh)

            concurrent_handler = ConcurrentRotatingFileHandler(
                filename=logfile_name, mode='a',
                maxBytes=5242880, backupCount=7, encoding='utf-8',
            )
            concurrent_handler.setFormatter(log_format)
            logger.addHandler(concurrent_handler)

        return logger


logs = HandleLogs.output_logs()
