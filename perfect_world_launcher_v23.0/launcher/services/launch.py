from __future__ import annotations

import os
import subprocess
import time
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QThread, Signal


class LaunchWorker(QObject):
    """Runs the account launch sequence off the UI thread."""

    log = Signal(str)
    finished = Signal()

    def __init__(self, accounts: List[Dict[str, str]], delay: int) -> None:
        super().__init__()
        self.accounts = accounts
        self.delay = delay

    def run(self) -> None:
        self.log.emit("Launch sequence started...")
        for idx, account in enumerate(self.accounts):
            login = account.get("login") or ""
            password = account.get("password") or ""
            character = account.get("character") or ""
            server_name = account.get("server_name") or "Unknown server"
            client_path = account.get("client_path") or ""
            if not login or not password or not character:
                self.log.emit(
                    f"Skipping account '{login or 'N/A'}' in {server_name} due to missing details."
                )
                continue
            try:
                command = [
                    client_path,
                    "startbypatcher",
                    f"user:{login}",
                    f"pwd:{password}",
                    f"role:{character}",
                ]
                subprocess.Popen(command, cwd=os.path.dirname(client_path) or None)
                self.log.emit(f"Launched account: {login} (Server: {server_name})")
                if idx < len(self.accounts) - 1 and self.delay > 0:
                    self.log.emit(f"Waiting for {self.delay:.1f} seconds...")
                    time.sleep(self.delay)
            except Exception as exc:  # pragma: no cover - best effort logging
                self.log.emit(
                    f"Failed to launch account {login} (Server: {server_name}): {exc}"
                )
        self.log.emit("Launch sequence finished.")
        self.finished.emit()


class LaunchService(QObject):
    """Coordinates the background launch worker and exposes lifecycle signals."""

    log = Signal(str)
    finished = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._thread: Optional[QThread] = None
        self._worker: Optional[LaunchWorker] = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None

    def start(self, accounts: List[Dict[str, str]], delay: int) -> None:
        if self.is_running:
            raise RuntimeError("Launch sequence is already running.")
        thread = QThread(self)
        worker = LaunchWorker(accounts, delay)
        worker.moveToThread(thread)
        worker.log.connect(self.log)
        worker.finished.connect(self._handle_worker_finished)
        thread.started.connect(worker.run)
        thread.finished.connect(self._cleanup)
        thread.start()
        self._thread = thread
        self._worker = worker

    def _handle_worker_finished(self) -> None:
        self.finished.emit()
        if self._thread is not None:
            self._thread.quit()

    def _cleanup(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        if self._thread is not None:
            self._thread.deleteLater()
            self._thread = None
