from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple, Union

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from launcher.models import AccountConfig, ServerConfig
from .theme import Theme, apply_button_style, apply_line_edit_style
from .run_checkbox import RunCheckBox

QWIDGETSIZE_MAX = 16777215

class ServerCard(QFrame):
    def __init__(self, window: "LauncherWindow") -> None:
        super().__init__(window)
        self.window = window
        self.index = -1
        self.accounts: List[Dict[str, QWidget]] = []
        self.expanded = True
        self.setObjectName("ServerCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            f"""
            QFrame#ServerCard {{
                background-color: {Theme.colors["surface"]};
                border-radius: {Theme.sizing["card_radius"]}px;
                border: 1px solid {Theme.colors["outline"]};
            }}
            """
        )
        outer_padding = window.section_padding
        inner_spacing = window.inner_spacing
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(
            outer_padding, outer_padding, outer_padding, outer_padding
        )
        root_layout.setSpacing(inner_spacing)
        header_frame = QFrame(self)
        header_frame.setObjectName("ServerCardHeader")
        header_frame.setAttribute(Qt.WA_StyledBackground, True)
        header_frame.setStyleSheet(
            "QFrame#ServerCardHeader { background-color: transparent; }"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(inner_spacing)
        self.toggle_button = QPushButton("Hide", header_frame)
        self.toggle_button.setFont(window.fonts["button"])
        apply_button_style(self.toggle_button, Theme.button_secondary)
        self.toggle_button.setFixedWidth(120)
        header_layout.addWidget(self.toggle_button)
        self.name_edit = QLineEdit(header_frame)
        self.name_edit.setFont(window.fonts["label"])
        apply_line_edit_style(self.name_edit)
        self.name_edit.setPlaceholderText("Server name")
        self.name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout.addWidget(self.name_edit)
        self.play_button = QPushButton("Play", header_frame)
        self.play_button.setFont(window.fonts["button"])
        apply_button_style(self.play_button, Theme.button_primary)
        self.play_button.setMinimumWidth(140)
        self.play_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        header_layout.addWidget(self.play_button)
        self.remove_button = QPushButton("Remove", header_frame)
        self.remove_button.setFont(window.fonts["button"])
        apply_button_style(self.remove_button, Theme.button_secondary)
        self.remove_button.setMinimumWidth(140)
        self.remove_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        header_layout.addWidget(self.remove_button)
        root_layout.addWidget(header_frame)
        self.body_widget = QWidget(self)
        self.body_widget.setObjectName("ServerCardBodyContainer")
        self.body_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.body_widget.setStyleSheet(
            "QWidget#ServerCardBodyContainer { background-color: transparent; }"
        )
        self.body_widget.setMinimumHeight(0)
        self.body_widget.setMaximumHeight(QWIDGETSIZE_MAX)
        self.body_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        body_container_layout = QVBoxLayout(self.body_widget)
        body_container_layout.setContentsMargins(0, 0, 0, 0)
        body_container_layout.setSpacing(0)
        self.body_content = QWidget(self.body_widget)
        self.body_content.setObjectName("ServerCardBody")
        self.body_content.setAttribute(Qt.WA_StyledBackground, True)
        self.body_content.setStyleSheet(
            "QWidget#ServerCardBody { background-color: transparent; }"
        )
        body_layout = QVBoxLayout(self.body_content)
        body_layout.setContentsMargins(0, inner_spacing, 0, inner_spacing)
        body_layout.setSpacing(inner_spacing)
        body_container_layout.addWidget(self.body_content)
        client_row = QHBoxLayout()
        client_row.setContentsMargins(0, 0, 0, 0)
        client_row.setSpacing(inner_spacing)
        self.client_path_label = QLabel("Client Path:", self.body_content)
        self.client_path_label.setFont(window.fonts["label"])
        self.client_path_label.setStyleSheet(
            f"color: {Theme.colors['muted']}; background-color: transparent;"
        )
        client_row.addWidget(self.client_path_label)
        self.client_path_edit = QLineEdit(self.body_content)
        self.client_path_edit.setFont(window.fonts["label"])
        apply_line_edit_style(self.client_path_edit)
        self.client_path_edit.setPlaceholderText("Select elementclient.exe")
        self.client_path_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        client_row.addWidget(self.client_path_edit)
        self.browse_button = QPushButton("Browse", self.body_content)
        self.browse_button.setFont(window.fonts["button"])
        apply_button_style(self.browse_button, Theme.button_secondary)
        self.browse_button.setFixedWidth(130)
        client_row.addWidget(self.browse_button)
        body_layout.addLayout(client_row)
        self.accounts_frame = QWidget(self.body_content)
        self.accounts_frame.setObjectName("ServerAccountsFrame")
        self.accounts_frame.setAttribute(Qt.WA_StyledBackground, True)
        self.accounts_frame.setStyleSheet(
            "QWidget#ServerAccountsFrame { background-color: transparent; }"
        )
        accounts_layout = QGridLayout(self.accounts_frame)
        accounts_layout.setContentsMargins(0, inner_spacing, 0, inner_spacing)
        accounts_layout.setHorizontalSpacing(inner_spacing)
        accounts_layout.setVerticalSpacing(inner_spacing)
        self.accounts_layout = accounts_layout
        headers = [
            ("Run?", 0, 80),
            ("Play", 0, 100),
            ("Login", 1, 200),
            ("Password", 1, 200),
            ("Character", 1, 180),
            ("Remove", 0, 130),
        ]
        for col, (text, stretch, min_width) in enumerate(headers):
            label = QLabel(text, self.accounts_frame)
            label.setFont(window.fonts["label_bold"])
            label.setStyleSheet(
                f"color: {Theme.colors['muted']}; background-color: transparent;"
            )
            label.setMinimumWidth(min_width)
            self.accounts_layout.addWidget(label, 0, col, alignment=Qt.AlignLeft)
            if stretch:
                self.accounts_layout.setColumnStretch(col, stretch)
            else:
                self.accounts_layout.setColumnMinimumWidth(col, min_width)
        body_layout.addWidget(self.accounts_frame)
        self.add_account_button = QPushButton("Add Account", self.body_content)
        self.add_account_button.setFont(window.fonts["button"])
        apply_button_style(self.add_account_button, Theme.button_secondary)
        self.add_account_button.setFixedWidth(150)
        body_layout.addWidget(self.add_account_button, alignment=Qt.AlignLeft)
        root_layout.addWidget(self.body_widget)
        self.body_widget.setMinimumHeight(0)
        self.body_animation = QPropertyAnimation(
            self.body_widget, b"maximumHeight", self
        )
        self.body_animation.setDuration(220)
        self.body_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.body_animation.finished.connect(self._on_body_animation_finished)
        self._pending_refresh = False
        self.toggle_button.clicked.connect(self.toggle_body)
        self.play_button.clicked.connect(self.play_server)
        self.remove_button.clicked.connect(self.remove_server)
        self.browse_button.clicked.connect(self.browse_client_path)
        self.add_account_button.clicked.connect(self.add_account)
        self.name_edit.textChanged.connect(self.on_name_changed)
        self.apply_config(ServerConfig())

    def populate_from_data(self, data: Dict[str, object]) -> None:
        self.apply_config(ServerConfig.from_mapping(data))

    def apply_config(self, config: Optional[ServerConfig] = None) -> None:
        config = config or ServerConfig()
        try:
            self.name_edit.blockSignals(True)
            self.name_edit.setText(config.name)
        finally:
            self.name_edit.blockSignals(False)
        self.client_path_edit.setText(config.client_path)
        self.clear_accounts()
        if config.accounts:
            for account in config.accounts:
                self.add_account(account, defer_layout=True)
        else:
            self.add_account(defer_layout=True)
        self.relayout_accounts()
        self.window.update_start_button_text()
        self._refresh_body_height()

    def set_index(self, index: int) -> None:
        self.index = index
        self.update_display_strings()

    def display_name(self) -> str:
        try:
            idx = self.window.servers.index(self)
        except ValueError:
            idx = self.index if self.index >= 0 else 0
        base_name = f"Server {idx + 1}"
        name = self.name_edit.text().strip()
        return name or base_name

    def client_path(self) -> str:
        return self.client_path_edit.text().strip()

    def toggle_body(self) -> None:
        self.set_expanded(not self.expanded, animate=False)

    def set_expanded(self, expanded: bool, *, animate: bool = False) -> None:
        if self.expanded == expanded:
            if not animate:
                self._refresh_body_height()
            return
        self.expanded = expanded
        self.toggle_button.setText("Hide" if self.expanded else "Show")
        if animate:
            self._animate_body(expanded)
        else:
            self._refresh_body_height()

    def _measure_body_height(self) -> int:
        was_visible = self.body_widget.isVisible()
        previous_max = self.body_widget.maximumHeight()
        self.body_widget.setVisible(True)
        self.body_widget.setMaximumHeight(QWIDGETSIZE_MAX)
        self.body_widget.ensurePolished()
        self.body_content.ensurePolished()
        self.body_content.adjustSize()
        hint = self.body_content.sizeHint().height()
        layout = self.body_widget.layout()
        if layout is not None:
            margins = layout.contentsMargins()
            hint += margins.top() + margins.bottom()
        self.body_widget.setMaximumHeight(previous_max)
        if not was_visible and not self.expanded:
            self.body_widget.setVisible(False)
        return max(hint, 0)

    def _animate_body(self, expanding: bool) -> None:
        animation = getattr(self, "body_animation", None)
        if animation is None:
            self._refresh_body_height()
            return
        animation.stop()
        self._pending_refresh = False
        current_height = max(self.body_widget.height(), 0)
        if expanding:
            target_height = max(self._measure_body_height(), current_height)
            self.body_widget.setVisible(True)
            self.body_widget.setMaximumHeight(max(target_height, 1))
            start_value = current_height
        else:
            if current_height <= 0:
                current_height = max(self._measure_body_height(), 1)
            self.body_widget.setVisible(True)
            self.body_widget.setMaximumHeight(max(current_height, 1))
            target_height = 0
            start_value = current_height
        animation.setStartValue(start_value)
        animation.setEndValue(target_height)
        animation.start()

    def _on_body_animation_finished(self) -> None:
        animation = getattr(self, "body_animation", None)
        if self.expanded:
            self.body_widget.setVisible(True)
            self.body_widget.setMaximumHeight(QWIDGETSIZE_MAX)
        else:
            self.body_widget.setMaximumHeight(0)
            self.body_widget.setVisible(False)
        if getattr(self, "_pending_refresh", False):
            self._pending_refresh = False
            self._refresh_body_height()
        elif animation is None or animation.state() != QPropertyAnimation.Running:
            self._refresh_body_height()

    def _refresh_body_height(self) -> None:
        animation = getattr(self, "body_animation", None)
        if animation and animation.state() == QPropertyAnimation.Running:
            self._pending_refresh = True
            return
        self._pending_refresh = False
        if self.expanded:
            self._measure_body_height()
            self.body_widget.setVisible(True)
            self.body_widget.setMaximumHeight(QWIDGETSIZE_MAX)
        else:
            self.body_widget.setMaximumHeight(0)
            self.body_widget.setVisible(False)

    def on_name_changed(self, _text: str) -> None:
        self.update_display_strings()

    def update_display_strings(self) -> None:
        display_name = self.display_name()
        self.client_path_label.setText(f"Client Path {display_name}:")
        self.play_button.setText(f"Play {display_name}")
        self.play_button.updateGeometry()
        self.remove_button.setText(f"Remove {display_name}")
        self.remove_button.updateGeometry()

    def play_server(self) -> None:
        if self.index < 0:
            return
        self.window.start_launch_sequence(server_index=self.index)

    def remove_server(self) -> None:
        self.window.remove_server(self)

    def handle_account_play(self, row: Dict[str, QWidget]) -> None:
        if self.index < 0:
            return
        try:
            account_index = self.accounts.index(row)
        except ValueError:
            return
        self.window.start_launch_sequence(
            server_index=self.index, account_index=account_index
        )

    def _create_account_button(
        self, text: str, style: Dict[str, object], *, width: Optional[int] = None
    ) -> QPushButton:
        button = QPushButton(text, self.accounts_frame)
        button.setFont(self.window.fonts["button"])
        apply_button_style(button, style)
        if width is not None:
            button.setFixedWidth(width)
        return button

    def _create_account_line_edit(
        self, placeholder: str, value: str = "", *, is_password: bool = False
    ) -> QLineEdit:
        line_edit = QLineEdit(self.accounts_frame)
        line_edit.setFont(self.window.fonts["label"])
        apply_line_edit_style(line_edit)
        line_edit.setPlaceholderText(placeholder)
        if is_password:
            line_edit.setEchoMode(QLineEdit.Password)
        line_edit.setText(value)
        return line_edit

    def _build_account_row(self, config: AccountConfig) -> Dict[str, QWidget]:
        run_switch = RunCheckBox(self.accounts_frame)
        run_switch.setChecked(config.run)
        run_switch.toggled.connect(
            lambda _checked: self.window.update_start_button_text()
        )
        play_button = self._create_account_button(
            "Play", Theme.button_primary, width=120
        )
        login_edit = self._create_account_line_edit("Login", config.login)
        password_edit = self._create_account_line_edit(
            "Password", config.password, is_password=True
        )
        character_edit = self._create_account_line_edit("Character", config.character)
        remove_button = self._create_account_button(
            "Remove", Theme.button_secondary, width=120
        )
        row_widgets: Dict[str, QWidget] = {
            "run": run_switch,
            "play": play_button,
            "login": login_edit,
            "password": password_edit,
            "character": character_edit,
            "remove": remove_button,
        }
        play_button.clicked.connect(
            lambda _checked=False, row=row_widgets: self.handle_account_play(row)
        )
        remove_button.clicked.connect(
            lambda _checked=False, row=row_widgets: self.remove_account(row)
        )
        return row_widgets

    def _place_account_row(self, row_index: int, row: Dict[str, QWidget]) -> None:
        self.accounts_layout.addWidget(row["run"], row_index, 0)
        self.accounts_layout.addWidget(row["play"], row_index, 1)
        self.accounts_layout.addWidget(row["login"], row_index, 2)
        self.accounts_layout.addWidget(row["password"], row_index, 3)
        self.accounts_layout.addWidget(row["character"], row_index, 4)
        self.accounts_layout.addWidget(row["remove"], row_index, 5)

    def add_account(
        self,
        account_data: Optional[Union[Dict[str, object], AccountConfig]] = None,
        *,
        defer_layout: bool = False,
    ) -> None:
        if isinstance(account_data, AccountConfig):
            config = account_data
        else:
            config = AccountConfig.from_mapping(account_data)
        row_widgets = self._build_account_row(config)
        self.accounts.append(row_widgets)
        if not defer_layout:
            self._place_account_row(len(self.accounts), row_widgets)
            self.window.update_start_button_text()
            self._refresh_body_height()

    def remove_account(self, row: Dict[str, QWidget]) -> None:
        if row not in self.accounts:
            return
        self.accounts.remove(row)
        for widget in row.values():
            self.accounts_layout.removeWidget(widget)
            widget.deleteLater()
        self.relayout_accounts()
        if not self.accounts:
            self.add_account()
        else:
            self.window.update_start_button_text()
        self._refresh_body_height()

    def clear_accounts(self) -> None:
        while self.accounts:
            row = self.accounts.pop()
            for widget in row.values():
                self.accounts_layout.removeWidget(widget)
                widget.deleteLater()
        self._refresh_body_height()

    def relayout_accounts(self) -> None:
        for row in self.accounts:
            for widget in row.values():
                self.accounts_layout.removeWidget(widget)
        for idx, row in enumerate(self.accounts, start=1):
            self._place_account_row(idx, row)
        self._refresh_body_height()

    def browse_client_path(self) -> None:
        initial_dir = self.window.base_dir
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select elementclient.exe",
            initial_dir,
            "Executable Files (*.exe);;All Files (*.*)",
        )
        if file_path:
            self.client_path_edit.setText(file_path)

    def _account_row_to_config(self, row: Dict[str, QWidget]) -> AccountConfig:
        return AccountConfig(
            login=row["login"].text(),
            password=row["password"].text(),
            character=row["character"].text(),
            run=row["run"].isChecked(),
        )

    def iter_account_configs(self) -> Iterable[AccountConfig]:
        for row in self.accounts:
            yield self._account_row_to_config(row)

    def selected_account_configs(self) -> Iterable[AccountConfig]:
        for config in self.iter_account_configs():
            if config.run:
                yield config

    def account_config_at(self, index: int) -> Optional[AccountConfig]:
        if 0 <= index < len(self.accounts):
            return self._account_row_to_config(self.accounts[index])
        return None

    def to_config(self) -> ServerConfig:
        return ServerConfig(
            name=self.name_edit.text(),
            client_path=self.client_path(),
            accounts=list(self.iter_account_configs()),
        )

    def count_selected_accounts(self) -> int:
        return sum(
            1
            for row in self.accounts
            if isinstance(row["run"], RunCheckBox) and row["run"].isChecked()
        )

    def accounts_count(self) -> int:
        return len(self.accounts)

    def set_launch_enabled(self, enabled: bool) -> None:
        self.play_button.setEnabled(enabled)
        for row in self.accounts:
            row["play"].setEnabled(enabled)


