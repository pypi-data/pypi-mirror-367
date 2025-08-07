from datetime import datetime

from .formatter import format_params


def format_datetime(epoch):
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


class FileHandler:
    def __init__(self, file):
        self.file = file

    def write_many(self, messages):
        with open(self.file, "a") as fp:
            for message in messages:
                timestamp = format_datetime(message.timestamp)
                params = format_params(message.params)
                fp.write(f"{timestamp} {message.level} {message.message} {params}\n")
