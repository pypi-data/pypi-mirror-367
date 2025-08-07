import os
from datetime import UTC, datetime
from typing import TypedDict

import requests

from .formatter import format_params

DATADOG_SITES = {
    "US1": "datadoghq.com",
    "US3": "us3.datadoghq.com",
    "US5": "us5.datadoghq.com",
    "EU1": "datadoghq.eu",
    "US1-FED": "ddog-gov.com",
    "AP1": "ap1.datadoghq.com",
}


class DatadogConfig(TypedDict, total=False):
    api_key: str
    site: str
    service: str
    tags: dict[str, str] | None


def get_datadog_endpoint(site):
    assert site in DATADOG_SITES
    return f"https://http-intake.logs.{DATADOG_SITES[site]}/api/v2/logs"


def format_tags(tags):
    if tags is None:
        return ""
    return ":".join(f"{k}:{v}" for k, v in tags.items())


def format_datetime(epoch):
    return datetime.fromtimestamp(epoch, UTC).strftime("%Y-%m-%dT%H:%M:%S,%f")[:-3]


class DatadogHandler:
    def __init__(self, config: DatadogConfig):
        self.api_key = config["api_key"]
        self.endpoint = get_datadog_endpoint(config["site"])
        self.service = config["service"]
        self.hostname = os.uname().nodename
        self.tags = format_tags(config.get("tags"))

    def write_many(self, messages):
        items = []
        for message in messages:
            timestamp = format_datetime(message.timestamp)
            params = format_params(message.params)
            items.append(
                {
                    "ddsource": "python",
                    "ddtags": self.tags,
                    "hostname": self.hostname,
                    "message": f"{timestamp} {message.level} {message.message} {params}",
                    "service": self.service,
                }
            )

        headers = {"DD-API-KEY": self.api_key}
        res = requests.post(
            self.endpoint,
            headers=headers,
            json=items,
            timeout=10,
        )
        if res.status_code != 202:
            print("datadog handler error", res.status_code, res.text)
