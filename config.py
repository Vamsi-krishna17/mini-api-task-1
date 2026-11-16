
import os
import math
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    countries_api: str
    frankfurter_api: str
    timeout: float


def load_settings() -> Settings:
    countries_api = os.getenv("COUNTRIES_API", "").strip()
    frankfurter_api = os.getenv("FRANKFURTER_API", "").strip()

    if not countries_api:
        raise ValueError(
            "Missing required setting: COUNTRIES_API"
        )

    if not frankfurter_api:
        raise ValueError(
            "Missing required setting: FRANKFURTER_API"
        )

    try:
        timeout = float(os.getenv("REQUEST_TIMEOUT", "10"))
    except ValueError as exc:
        raise ValueError(
            "REQUEST_TIMEOUT must be a valid number."
        ) from exc

    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError(
            "REQUEST_TIMEOUT must be greater than zero."
        )

    return Settings(
        countries_api=countries_api.rstrip("/"),
        frankfurter_api=frankfurter_api.rstrip("/"),
        timeout=timeout,
    )


settings = load_settings()
