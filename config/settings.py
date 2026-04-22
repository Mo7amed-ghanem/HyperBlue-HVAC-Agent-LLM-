from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    planner_model: str = os.getenv("PLANNER_MODEL", "gemini-2.5-flash")
    hvac_model: str = os.getenv("HVAC_MODEL", "gemini-2.5-flash")


settings = Settings()
