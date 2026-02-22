from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AccountConfig:
    login: str = ""
    password: str = ""
    character: str = ""
    run: bool = True

    @classmethod
    def from_mapping(cls, data: Optional[Dict[str, object]]) -> "AccountConfig":
        if not data:
            return cls()
        login = data.get("login") if isinstance(data, dict) else None
        password = data.get("password") if isinstance(data, dict) else None
        character = data.get("character") if isinstance(data, dict) else None
        run = data.get("run", True) if isinstance(data, dict) else True
        return cls(
            login="" if login is None else str(login),
            password="" if password is None else str(password),
            character="" if character is None else str(character),
            run=bool(run),
        )

    def to_payload(self) -> Dict[str, object]:
        return {
            "run": self.run,
            "login": self.login,
            "password": self.password,
            "character": self.character,
        }

    def to_launch_payload(self, server_name: str, client_path: str) -> Dict[str, str]:
        return {
            "server_name": server_name,
            "client_path": client_path,
            "login": self.login.strip(),
            "password": self.password,
            "character": self.character.strip(),
        }
