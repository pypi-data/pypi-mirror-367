import sys
from datetime import datetime

from .formatter import format_params
from .levels import LEVEL_ERROR, LEVEL_WARN

COLOR_YELLOW = "\033[1;33m"
COLOR_RED = "\033[0;31m"
COLOR_RESET = "\033[0m"


def format_datetime(epoch):
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


class ConsoleHandler:
    def add(self, message):
        timestamp = format_datetime(message.timestamp)
        params = format_params(message.params)
        if message.level == LEVEL_ERROR:
            color = COLOR_RED
        elif message.level == LEVEL_WARN:
            color = COLOR_YELLOW
        else:
            color = ""

        sys.stdout.write(
            f"{color}{timestamp} - {message.message} {params}{COLOR_RESET}\n"
        )
        sys.stdout.flush()
