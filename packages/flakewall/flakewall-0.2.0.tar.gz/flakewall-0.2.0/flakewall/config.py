from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml


DEFAULT_CONFIG = {
    "retries": 0,
    "report_glob": "**/junit*.xml",
}

CONFIG_DIR = Path(".flakewall")
CONFIG_PATH = CONFIG_DIR / "config.yml"
QUARANTINE_PATH = CONFIG_DIR / "quarantine.yml"


@dataclass
class FlakewallConfig:
    retries: int = 0
    report_glob: str = "**/junit*.xml"

    @staticmethod
    def load(path: Optional[Path] = None) -> "FlakewallConfig":
        target_path = path or CONFIG_PATH
        if not target_path.exists():
            return FlakewallConfig()
        data = yaml.safe_load(target_path.read_text()) or {}
        return FlakewallConfig(
            retries=int(data.get("retries", 0)),
            report_glob=str(data.get("report_glob", "**/junit*.xml")),
        )

    def save(self, path: Optional[Path] = None) -> None:
        target_path = path or CONFIG_PATH
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "retries": self.retries,
            "report_glob": self.report_glob,
        }
        target_path.write_text(yaml.safe_dump(payload, sort_keys=True))


def ensure_default_files() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        FlakewallConfig().save(CONFIG_PATH)
    if not QUARANTINE_PATH.exists():
        QUARANTINE_PATH.write_text(yaml.safe_dump({"quarantined": []}, sort_keys=True))
