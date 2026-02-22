from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from launcher.models import AccountConfig, ServerConfig


class SettingsError(Exception):
    """Raised when persisting settings data fails."""


@dataclass
class SettingsLoadResult:
    delay: int
    servers: List[ServerConfig]
    message: str
    warnings: List[str] = field(default_factory=list)
    source_path: Optional[Path] = None


@dataclass
class SettingsSaveResult:
    path: Path
    message: str


class SettingsStore:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.settings_dir, self.settings_file = self._resolve_settings_paths(base_dir)

    def load(self, filepath: Optional[str] = None) -> SettingsLoadResult:
        path = Path(filepath) if filepath else Path(self.settings_file)
        try:
            with path.open("r", encoding="utf-8") as handle:
                raw_settings = json.load(handle)
        except FileNotFoundError:
            return SettingsLoadResult(
                delay=3,
                servers=[],
                message="No settings file found. Starting with default configuration.",
                source_path=path,
            )
        except (json.JSONDecodeError, KeyError) as exc:
            return SettingsLoadResult(
                delay=3,
                servers=[],
                message=f"Error reading settings file: {exc}. Loading defaults.",
                warnings=[str(exc)],
                source_path=path,
            )

        delay_value = raw_settings.get("delay", 3)
        try:
            delay_int = int(float(delay_value))
            delay_int = max(delay_int, 1)
        except (TypeError, ValueError):
            delay_int = 3

        servers: List[ServerConfig] = []
        servers_data = raw_settings.get("servers")
        if isinstance(servers_data, list) and servers_data:
            for server_entry in servers_data:
                if isinstance(server_entry, dict):
                    servers.append(ServerConfig.from_mapping(server_entry))
        else:
            legacy_accounts = raw_settings.get("accounts")
            if isinstance(legacy_accounts, list):
                accounts = [
                    AccountConfig.from_mapping(entry)
                    for entry in legacy_accounts
                    if isinstance(entry, dict)
                ]
                legacy_config = ServerConfig(
                    name=str(raw_settings.get("server_name") or "Server 1"),
                    client_path=str(raw_settings.get("client_path", "")),
                    accounts=accounts,
                )
                servers.append(legacy_config)

        message = f"Settings loaded from {path.name}" if path.exists() else "Loaded settings"
        return SettingsLoadResult(
            delay=delay_int,
            servers=servers,
            message=message,
            source_path=path,
        )

    def save(
        self,
        delay: int,
        servers: List[ServerConfig],
        filepath: Optional[str] = None,
    ) -> SettingsSaveResult:
        target_path = Path(filepath) if filepath else Path(self.settings_file)
        payload = {
            "delay": max(1, int(delay)),
            "servers": [config.to_payload() for config in servers],
        }
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with target_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=4)
        except Exception as exc:  # pragma: no cover - surface to UI layer
            raise SettingsError(
                f"Could not save settings to {target_path}: {exc}"
            ) from exc
        return SettingsSaveResult(path=target_path, message=f"Settings saved to {target_path.name}")

    def _resolve_settings_paths(self, base_dir: str) -> tuple[str, str]:
        default_dir = base_dir
        default_file = os.path.join(default_dir, "settings.json")
        if self._dir_is_writable(default_dir):
            return default_dir, default_file
        fallback_root = os.getenv("APPDATA") or os.path.expanduser("~")
        fallback_dir = os.path.join(fallback_root, "PerfectWorldLauncher")
        try:
            os.makedirs(fallback_dir, exist_ok=True)
        except Exception:
            fallback_dir = default_dir
        fallback_file = os.path.join(fallback_dir, "settings.json")
        if os.path.isfile(default_file) and not os.path.isfile(fallback_file):
            try:
                shutil.copy2(default_file, fallback_file)
            except Exception:
                pass
        return fallback_dir, fallback_file

    def _dir_is_writable(self, directory: str) -> bool:
        try:
            test_path = Path(directory) / "._pwlauncher_write_test"
            test_path.parent.mkdir(parents=True, exist_ok=True)
            with test_path.open("w", encoding="utf-8") as tmp:
                tmp.write("ok")
            test_path.unlink(missing_ok=True)
            return True
        except Exception:
            return False
