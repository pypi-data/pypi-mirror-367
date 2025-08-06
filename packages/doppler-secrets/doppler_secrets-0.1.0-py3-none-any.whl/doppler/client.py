import logging
import os
import re
import json
import uuid
from datetime import datetime
import requests
from cachetools.func import ttl_cache

logger = logging.getLogger(__name__)


class Doppler:
    def __init__(self, project: str, config: str, token: str = None, ttl: int = 60 * 60):
        self.project: str = project
        self.config: str = config
        self.token: str = token or os.getenv("DOPPLER_TOKEN")
        self.ttl: int = ttl

    @property
    def url(self):
        return "https://api.doppler.com/v3/configs/config/secrets"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @property
    def params(self):
        return {
            "project": self.project,
            "config": self.config,
        }

    @ttl_cache(ttl=60 * 60)
    def _get(self) -> dict:
        logger.info("%s/%s > fetching secrets", self.project, self.config)

        response = requests.get(
            self.url,
            headers=self.headers,
            params=self.params,
        )

        if response.status_code != 200:
            logger.error("%s/%s > failed to fetch secrets: %s", self.project, self.config, response.text)
            response.raise_for_status()

        return response.json()

    def get(self, name: str) -> object:
        secrets = self._get()["secrets"]

        try:
            secret = secrets[name]
            value = secret["computed"]
            type = secret["computedValueType"]["type"]

            if type == "boolean":
                return value.lower() == "true"
            elif type == "integer":
                return int(value)
            elif type == "decimal":
                return float(value)
            elif type == "date8601":
                return datetime.strptime(value, "%Y-%m-%d").date()
            elif type == "datetime8601":
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
            elif type.startswith("uuid"):
                return uuid.UUID(value)
            elif type.startswith("json"):
                return json.loads(value)
            else:
                return value
        except KeyError:
            raise KeyError(f"{name} is not a valid secret")

    def __getattribute__(self, name: str):
        if bool(re.fullmatch(r"[A-Z_]+", name)):
            return self.get(name)

        return super().__getattribute__(name)

    def __getitem__(self, name: str) -> object:
        return self.get(name)
