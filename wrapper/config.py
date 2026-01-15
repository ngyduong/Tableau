from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(frozen=True)
class TabCredentials:
    pat_name: str
    pat_secret: str
    site_id: str
    site_url: str
    api_version: Optional[str] = None


class ConfigWrapper(metaclass=Singleton):
    """
    Centralised config access.
    Loaded once, reused everywhere.
    """

    def __init__(self) -> None:
        self.tab_cred = TabCredentials(
            pat_name=os.getenv("TAB_PAT_NAME", ""),
            pat_secret=os.getenv("TAB_PAT_SECRET", ""),
            site_id=os.getenv("TAB_SITE_ID", ""),
            site_url=os.getenv("TAB_SITE_URL", ""),
            api_version=os.getenv("TAB_API_VERSION"),
        )
        self._validate()

    def _validate(self) -> None:
        missing = [
            name
            for name, value in vars(self.tab_cred).items()
            if name != "api_version" and not value
        ]
        if missing:
            raise ValueError(f"Missing Tableau config vars: {missing}")
