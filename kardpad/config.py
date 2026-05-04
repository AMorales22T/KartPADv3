from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "KartPADv3"
VERSION  = "3.1.0"
HTTP_PORT = 3000
WS_PORT = 8000
UDP_PORT = 26760


def _resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _data_root() -> Path:
    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        base_dir = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base_dir / APP_NAME
    return Path(__file__).resolve().parent.parent


RESOURCE_DIR = _resource_root()
DATA_DIR = _data_root()
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = RESOURCE_DIR / "static"

PLAYER_COUNT = 4
DSU_PROTOCOL_VERSION = 1001
DSU_SERVER_ID = 0x4B504144  # "KPAD"
DSU_MESSAGE_VERSION = 0x100000
DSU_MESSAGE_PORTS = 0x100001
DSU_MESSAGE_DATA = 0x100002
DSU_CLIENT_TIMEOUT_SECONDS = 15.0  # era 5.0 — demasiado agresivo con carga de CPU
DSU_BROADCAST_HZ = 60.0
MOTION_DEBUG = False  # True para logs de telemetría de movimiento
