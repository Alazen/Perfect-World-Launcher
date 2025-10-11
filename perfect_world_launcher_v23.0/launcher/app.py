from __future__ import annotations

import sys

try:
    from PySide6.QtWidgets import QApplication
except ImportError as exc:  # pragma: no cover - UI dependency
    raise ImportError(
        "PySide6 is required to run this application. Install it with 'pip install PySide6'."
    ) from exc

try:
    from .resources import app_icon_rc  # noqa: F401  # Ensure Qt resources are registered
except ImportError:
    app_icon_rc = None

from .ui.window import LauncherWindow


def run() -> None:
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())
