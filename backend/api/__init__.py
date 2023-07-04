import os
import tomllib
from pathlib import Path
from typing import Optional

CREDENTIALS_PATH = os.environ.get("API_CREDENTIALS") or Path(__file__).parent


def load_credentials(key: str, values: list[str]) -> Optional[list[str]]:
    try:
        with open(f"{CREDENTIALS_PATH}/credentials.toml", "rb") as stream:
            config = tomllib.load(stream)
    except FileNotFoundError:
        raise Exception("Missing file with the credentials!")

    try:
        return [config[key][value] for value in values]
    except KeyError:
        return None
