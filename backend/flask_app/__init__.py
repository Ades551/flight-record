import os
from pathlib import Path
from typing import Callable, Optional

import requests
from flask import Flask, send_from_directory
from threads import flights, lock

PATH_TO_APP = Path(__file__).parent
MP3_PATH = PATH_TO_APP / "static" / "data" / "mp3"
TRANSCRIPT_PATH = PATH_TO_APP / "static" / "data" / "transcript"
REACT_PATH = (PATH_TO_APP / "static" / "react").absolute()


def get_pub_ip() -> Optional[str]:
    prefix: Callable[[str], str] = lambda x: f"http://{x}"

    if os.environ.get("FLASK_USE_PUB_IP") == "true":
        if ip := os.environ.get("FLASK_PUB_IP"):
            return prefix(ip)

        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            return prefix(response.text)

    return None


PORT = (int(port) if (port := os.environ.get("FLASK_PORT")) else None) or 5000
API_URL = get_pub_ip() or "http://127.0.0.1"

app = Flask(__name__)


def get_api_url(static: str) -> str:
    return f"{API_URL.removesuffix('/')}:{PORT}/{static.removeprefix('/')}"


# Serve React App
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and Path(REACT_PATH / path).exists():
        return send_from_directory(REACT_PATH, path)
    else:
        return send_from_directory(REACT_PATH, "index.html")


def create_paths() -> None:
    MP3_PATH.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_PATH.mkdir(parents=True, exist_ok=True)
    REACT_PATH.mkdir(parents=True, exist_ok=True)


def create_app() -> Flask:
    create_paths()

    from .api.api import api

    app.register_blueprint(api, url_prefix="/api")

    return app


__all__ = ("flights", "lock")
