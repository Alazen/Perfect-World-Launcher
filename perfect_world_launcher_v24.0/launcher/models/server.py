from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .account import AccountConfig


@dataclass
class ServerConfig:
    name: str = ""
    client_path: str = ""
    accounts: List[AccountConfig] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Optional[Dict[str, object]]) -> "ServerConfig":
        if not data or not isinstance(data, dict):
            return cls()
        raw_accounts = data.get("accounts")
        accounts: List[AccountConfig] = []
        if isinstance(raw_accounts, list):
            for entry in raw_accounts:
                if isinstance(entry, dict):
                    accounts.append(AccountConfig.from_mapping(entry))
        name = data.get("name")
        client_path = data.get("client_path")
        return cls(
            name="" if name is None else str(name),
            client_path="" if client_path is None else str(client_path),
            accounts=accounts,
        )

    def to_payload(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "client_path": self.client_path,
            "accounts": [account.to_payload() for account in self.accounts],
        }
