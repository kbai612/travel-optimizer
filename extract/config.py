"""Loads destinations.yml into typed config used by every extractor."""

from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()  # populate os.environ from a local .env before any extractor reads credentials

REPO_ROOT = Path(__file__).resolve().parent.parent
DESTINATIONS_PATH = REPO_ROOT / "config" / "destinations.yml"
BRONZE_DIR = REPO_ROOT / "data" / "bronze"


class Destination(BaseModel):
    name: str
    iata: str
    icao: str
    country: str
    lat: float
    lon: float


def load_destinations(path: Path = DESTINATIONS_PATH) -> list[Destination]:
    raw = yaml.safe_load(path.read_text())
    return [Destination(**d) for d in raw["destinations"]]


def bronze_path(source: str, iata: str, filename: str) -> Path:
    """data/bronze/<source>/<iata>/<filename>, creating parent dirs as needed."""
    out_dir = BRONZE_DIR / source / iata
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / filename
