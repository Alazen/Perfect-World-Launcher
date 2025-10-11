from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)

from ..models import AccountConfig, ServerConfig
from ..services import LaunchService, SettingsError, SettingsStore
from .delay_stepper import DelayStepper
from .server_card import ServerCard
from .theme import Theme, apply_button_style, apply_plain_text_style

RESOURCE_ICON_ID = ':/launcher/icons/pw_launcher_icon_3.ico'

class LauncherWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Perfect World Launcher")
        self.resize(1120, 700)
        self.setMinimumSize(1120, 500)
        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.section_padding = Theme.sizing["section_padding"]
        self.inner_spacing = self.section_padding // 2
        self._reserved_scrollbar_width = 0
        self._current_scrollbar_margin = -1
        self.fonts = {
            "heading": self._create_font(16, bold=True),
            "label": self._create_font(10),
            "label_bold": self._create_font(10, bold=True),
            "button": self._create_font(10, bold=True),
        }
        self.servers: List[ServerCard] = []
        self.log_panel_visible = False
        self.launching = False
        self.settings_store = SettingsStore(self.base_dir)
        self.launch_service = LaunchService(self)
        self.launch_service.log.connect(self.log)
        self.launch_service.finished.connect(self._on_launch_finished)
        self._apply_window_icon()
        self._build_ui()
        self.load_settings()

    def _create_font(self, size: int, *, bold: bool = False) -> QFont:
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        return font

    def _apply_window_icon(self) -> None:
        icon = QIcon(RESOURCE_ICON_ID)
        if icon.isNull():
            fallback_path = self._resolve_icon_path()
            if fallback_path is None:
                return
            icon = QIcon(str(fallback_path))
        self.setWindowIcon(icon)
        app = QApplication.instance()
        if app is not None:
            app.setWindowIcon(icon)

    def _resolve_icon_path(self) -> Optional[Path]:
        search_roots: List[Path] = []
        base_path = Path(self.base_dir)
        search_roots.append(base_path)
        module_path = Path(__file__).resolve()
        search_roots.extend(module_path.parents)
        seen: Set[str] = set()
        for root in search_roots:
            candidate = root / 'assets' / 'pw_launcher_icon_3.ico'
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            if candidate.exists():
                return candidate
        return None

    def _build_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {Theme.colors["bg"]};
            }}
            QWidget {{
                color: {Theme.colors["text"]};
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QFrame#LogFrame {{
                background-color: {Theme.colors["surface"]};
                border-radius: {Theme.sizing["card_radius"]}px;
                border: 1px solid {Theme.colors["outline"]};
            }}
            QPushButton {{
                border-radius: {Theme.sizing["pill_radius"]}px;
            }}
            QLineEdit {{
                border-radius: {Theme.sizing["pill_radius"]}px;
            }}
            QPlainTextEdit {{
                border-radius: {Theme.sizing["inner_radius"]}px;
            }}
            QWidget#ServersContainer {{
                background-color: {Theme.colors["bg"]};
            }}
            """
        )
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(
            self.section_padding,
            self.section_padding,
            self.section_padding,
            self.section_padding,
        )
        main_layout.setSpacing(self.inner_spacing)
        settings_frame = QFrame(central)
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(self.inner_spacing)
        self.import_button = QPushButton("Import Settings", settings_frame)
        self.import_button.setFont(self.fonts["button"])
        apply_button_style(self.import_button, Theme.button_secondary)
        settings_layout.addWidget(self.import_button)
        self.export_button = QPushButton("Export Settings", settings_frame)
        self.export_button.setFont(self.fonts["button"])
        apply_button_style(self.export_button, Theme.button_secondary)
        settings_layout.addWidget(self.export_button)
        settings_layout.addStretch(1)
        delay_controls = QWidget(settings_frame)
        delay_controls_layout = QHBoxLayout(delay_controls)
        delay_controls_layout.setContentsMargins(0, 0, 0, 0)

        self.delay_label = QLabel("Delay (s):", delay_controls)
        self.delay_label.setFont(self.fonts["label"])
        self.delay_label.setStyleSheet(f"color: {Theme.colors['muted']};")
        delay_controls_layout.addWidget(self.delay_label)

        self.delay_stepper = DelayStepper(delay_controls)
        self.delay_stepper.setFont(self.fonts["label"])
        self.delay_stepper.setValue(3)

        delay_controls_layout.setSpacing(self.delay_stepper.display_padding)
        delay_controls_layout.addWidget(self.delay_stepper)

        settings_layout.addWidget(delay_controls)
        main_layout.addWidget(settings_frame)
        self.scroll_area = QScrollArea(central)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.servers_container = QWidget()
        self.servers_container.setObjectName("ServersContainer")
        self.servers_layout = QVBoxLayout(self.servers_container)
        self.servers_layout.setContentsMargins(0, 0, 0, 0)
        self.servers_layout.setSpacing(self.inner_spacing)
        self.servers_spacer = QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.servers_layout.addItem(self.servers_spacer)
        self.scroll_area.setWidget(self.servers_container)
        self.scroll_area.viewport().setStyleSheet(
            f"background-color: {Theme.colors['bg']};"
        )
        self._reserved_scrollbar_width = self.scroll_area.style().pixelMetric(
            QStyle.PM_ScrollBarExtent
        )
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.rangeChanged.connect(self._update_scrollbar_margin)
        scrollbar.valueChanged.connect(self._update_scrollbar_margin)
        self._update_scrollbar_margin()
        main_layout.addWidget(self.scroll_area, stretch=1)
        controls_frame = QFrame(central)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(self.inner_spacing)
        self.start_button = QPushButton("Start 0 accounts", controls_frame)
        self.start_button.setFont(self.fonts["button"])
        apply_button_style(self.start_button, Theme.button_primary)
        controls_layout.addWidget(self.start_button)
        self.add_server_button = QPushButton("Add Server", controls_frame)
        self.add_server_button.setFont(self.fonts["button"])
        apply_button_style(self.add_server_button, Theme.button_secondary)
        controls_layout.addWidget(self.add_server_button)
        self.save_close_button = QPushButton("Save and Close", controls_frame)
        self.save_close_button.setFont(self.fonts["button"])
        apply_button_style(self.save_close_button, Theme.button_secondary)
        controls_layout.addWidget(self.save_close_button)
        self.toggle_log_button = QPushButton("Show Log", controls_frame)
        self.toggle_log_button.setFont(self.fonts["button"])
        apply_button_style(self.toggle_log_button, Theme.button_secondary)
        controls_layout.addWidget(self.toggle_log_button)
        main_layout.addWidget(controls_frame)
        self.log_frame = QFrame(central)
        self.log_frame.setObjectName("LogFrame")
        log_layout = QVBoxLayout(self.log_frame)
        log_layout.setContentsMargins(
            self.inner_spacing,
            self.inner_spacing,
            self.inner_spacing,
            self.inner_spacing,
        )
        log_layout.setSpacing(self.inner_spacing)
        self.log_textbox = QPlainTextEdit(self.log_frame)
        apply_plain_text_style(self.log_textbox)
        log_layout.addWidget(self.log_textbox)
        self.log_frame.setVisible(False)
        main_layout.addWidget(self.log_frame)
        self.status_bar = QLabel("Ready.", central)
        self.status_bar.setFont(self.fonts["label"])
        self.status_bar.setStyleSheet(f"color: {Theme.colors['muted']};")
        main_layout.addWidget(self.status_bar)
        self.import_button.clicked.connect(self.import_settings)
        self.export_button.clicked.connect(self.export_settings)
        self.add_server_button.clicked.connect(self.add_server)
        self.start_button.clicked.connect(lambda: self.start_launch_sequence())
        self.save_close_button.clicked.connect(self.save_and_close)
        self.toggle_log_button.clicked.connect(self.toggle_log_panel)
        self.update_start_button_text()

    def _update_scrollbar_margin(self, *_: int) -> None:
        scrollbar = self.scroll_area.verticalScrollBar()
        if self.scroll_area.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOn:
            margin = 0
        else:
            width = max(self._reserved_scrollbar_width, scrollbar.sizeHint().width(), 0)
            needs_scrollbar = scrollbar.maximum() > 0
            margin = 0 if needs_scrollbar else width
        if margin != self._current_scrollbar_margin:
            self.scroll_area.setViewportMargins(0, 0, margin, 0)
            self._current_scrollbar_margin = margin

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_scrollbar_margin()

    def add_server(
        self, server_data: Optional[Union[Dict[str, object], ServerConfig]] = None
    ) -> ServerCard:
        card = ServerCard(self)
        insert_index = max(0, self.servers_layout.count() - 1)
        self.servers_layout.insertWidget(insert_index, card)
        self.servers.append(card)
        if server_data:
            config = (
                server_data
                if isinstance(server_data, ServerConfig)
                else ServerConfig.from_mapping(server_data)
            )
            card.apply_config(config)
        self.reindex_servers()
        self._update_scrollbar_margin()
        return card

    def remove_server(self, card: ServerCard) -> None:
        if card not in self.servers:
            return
        server_name = card.display_name()
        self.servers.remove(card)
        self.servers_layout.removeWidget(card)
        card.deleteLater()
        if not self.servers:
            self.add_server()
        self.reindex_servers()
        self._update_scrollbar_margin()
        self.log(f"Removed {server_name}")

    def clear_servers(self) -> None:
        for card in list(self.servers):
            self.servers_layout.removeWidget(card)
            card.deleteLater()
        self.servers.clear()
        self._update_scrollbar_margin()

    def reindex_servers(self) -> None:
        for idx, card in enumerate(self.servers):
            card.set_index(idx)
        self.update_start_button_text()

    def load_settings(self, filepath: Optional[str] = None) -> None:
        self.clear_servers()
        result = self.settings_store.load(filepath)
        self.delay_stepper.setValue(result.delay)
        if result.servers:
            for server_config in result.servers:
                self.add_server(server_config)
        else:
            self.add_server()
        if result.message:
            self.log(result.message)
        for warning in result.warnings:
            self.log(warning)
        self.update_start_button_text()

    def save_settings(
        self, filepath: Optional[str] = None, *, show_message: bool = False
    ) -> bool:
        server_configs = [card.to_config() for card in self.servers]
        try:
            result = self.settings_store.save(
                self.delay_stepper.value(), server_configs, filepath
            )
        except SettingsError as exc:
            message = str(exc)
            self.log(message)
            if show_message:
                QMessageBox.critical(self, "Save Failed", message)
            return False
        self.log(result.message)
        if show_message:
            QMessageBox.information(
                self,
                "Save Complete",
                f"Settings saved to:\n\n{result.path}",
            )
        return True

    def import_settings(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            self.settings_store.settings_dir,
            "JSON Files (*.json);;All Files (*.*)",
        )
        if filepath:
            self.load_settings(filepath)
            self._update_scrollbar_margin()

    def export_settings(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            self.settings_store.settings_dir,
            "JSON Files (*.json);;All Files (*.*)",
        )
        if filepath:
            if not filepath.lower().endswith(".json"):
                filepath += ".json"
            self.save_settings(filepath, show_message=True)

    def save_and_close(self) -> None:
        if self.launch_service.is_running:
            QMessageBox.warning(
                self,
                "Launch In Progress",
                "Please wait for the launch sequence to finish.",
            )
            return
        if self.save_settings(show_message=True):
            self.close()

    def toggle_log_panel(self) -> None:
        self.log_panel_visible = not self.log_panel_visible
        self.log_frame.setVisible(self.log_panel_visible)
        self.toggle_log_button.setText(
            "Hide Log" if self.log_panel_visible else "Show Log"
        )
        self._update_scrollbar_margin()

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_message = f"{timestamp} {message}"
        self.status_bar.setText(log_message)
        self.log_textbox.appendPlainText(log_message)
        scrollbar = self.log_textbox.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def get_delay_value(self) -> int:
        return self.delay_stepper.value()


    def collect_launch_plan(
        self, server_index: Optional[int] = None, account_index: Optional[int] = None
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        accounts: List[Dict[str, str]] = []
        errors: List[str] = []
        if server_index is not None:
            if not (0 <= server_index < len(self.servers)):
                return [], ["Selected server does not exist."]
            servers_iter: List[Tuple[int, ServerCard]] = [
                (server_index, self.servers[server_index])
            ]
        else:
            servers_iter = list(enumerate(self.servers))
        forced_account = account_index is not None
        for idx, card in servers_iter:
            server_name = card.display_name()
            client_path = card.client_path()
            if not client_path or not Path(client_path).is_file():
                errors.append(f"Client path for '{server_name}' is invalid or missing.")
                continue
            if forced_account and idx == server_index:
                config = (
                    card.account_config_at(account_index)
                    if account_index is not None
                    else None
                )
                if config is None:
                    errors.append(
                        f"Selected account does not exist in '{server_name}'."
                    )
                    target_accounts: List[AccountConfig] = []
                else:
                    target_accounts = [config]
            else:
                target_accounts = list(card.selected_account_configs())
            for account_config in target_accounts:
                accounts.append(
                    account_config.to_launch_payload(server_name, client_path)
                )
        return accounts, errors

    def start_launch_sequence(
        self, server_index: Optional[int] = None, account_index: Optional[int] = None
    ) -> None:
        if self.launch_service.is_running:
            QMessageBox.warning(
                self, "Launch In Progress", "A launch sequence is already running."
            )
            return
        self.save_settings()
        delay = self.get_delay_value()
        accounts_to_launch, errors = self.collect_launch_plan(
            server_index, account_index
        )
        if errors:
            for error in errors:
                self.log(error)
            if not accounts_to_launch:
                QMessageBox.critical(self, "Invalid Configuration", "\n".join(errors))
                return
        if not accounts_to_launch:
            self.log("No accounts selected or configured to launch.")
            return
        self.start_launching(accounts_to_launch, delay)

    def start_launching(self, accounts: List[Dict[str, str]], delay: int) -> None:
        if self.launch_service.is_running:
            return
        self.launching = True
        self.set_launch_controls_enabled(False)
        try:
            self.launch_service.start(accounts, delay)
        except RuntimeError as exc:
            self.log(str(exc))
            self.launching = False
            self.set_launch_controls_enabled(True)

    def _on_launch_finished(self) -> None:
        self.launching = False
        self.set_launch_controls_enabled(True)

    def set_launch_controls_enabled(self, enabled: bool) -> None:
        self.start_button.setEnabled(enabled)
        for card in self.servers:
            card.set_launch_enabled(enabled)

    def update_start_button_text(self) -> None:
        total = sum(card.count_selected_accounts() for card in self.servers)
        label = f"Start {total} account{'s' if total != 1 else ''}"
        self.start_button.setText(label)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.launch_service.is_running:
            QMessageBox.warning(
                self,
                "Launch In Progress",
                "Please wait for the launch sequence to finish.",
            )
            event.ignore()
            return
        if self.save_settings():
            event.accept()
        else:
            choice = QMessageBox.question(
                self,
                "Exit Without Saving",
                "Settings were not saved. Exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if choice == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
