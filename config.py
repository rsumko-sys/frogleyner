import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    db_path: str = "leinerfrog.db"
    openweather_api_key: str = ""
    weather_city: str = "Kyiv"
    host_user_id: int = 0  # Telegram user_id хазяїна — персоналізація для нього


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")
    host = 0
    for key in ("HOST_USER_ID", "OWNER_ID"):
        v = os.getenv(key, "").strip()
        if v and v.isdigit():
            host = int(v)
            break
    return Config(
        bot_token=token,
        db_path=os.getenv("DB_PATH", "leinerfrog.db"),
        openweather_api_key=os.getenv("OPENWEATHER_API_KEY", "") or os.getenv("WEATHER_API_KEY", ""),
        weather_city=os.getenv("WEATHER_CITY", "Kyiv"),
        host_user_id=host,
    )
