from __future__ import annotations

from typing import Optional, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from .theme import Theme, lighten


class DelayStepper(QWidget):
    """Compact +/- stepper to choose an integer delay with a minimum."""

    valueChanged = Signal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        minimum: int = 1,
        maximum: Optional[int] = None,
        initial: int = 3,
    ) -> None:
        super().__init__(parent)
        self._minimum = max(1, int(minimum))
        self._maximum = int(maximum) if maximum is not None else None
        self._value = max(self._minimum, int(initial))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._display_padding = max(4, Theme.sizing["entry_height"] // 6)
        layout.setSpacing(self._display_padding)

        self.value_display = QLabel(str(self._value), self)
        self.value_display.setAlignment(Qt.AlignCenter)
        self.value_display.setFixedHeight(Theme.sizing["entry_height"])
        self.value_display.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.value_display.setContentsMargins(
            self._display_padding,
            0,
            self._display_padding,
            0,
        )
        self.value_display.setStyleSheet(
            f"color: {Theme.colors['text']}; background-color: transparent; border: none;"
        )
        layout.addWidget(self.value_display)

        metrics = self.value_display.fontMetrics()
        self._minimum_display_width = (
            metrics.horizontalAdvance("00") + 2 * self._display_padding
        )

        buttons_frame = QWidget(self)
        buttons_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(self._display_padding)

        self.decrease_button = self._make_button("-", self._handle_decrease, segment="left")
        buttons_layout.addWidget(self.decrease_button)

        self.increase_button = self._make_button("+", self._handle_increase, segment="right")
        buttons_layout.addWidget(self.increase_button)

        layout.addWidget(buttons_frame)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._update_state()

    @property
    def display_padding(self) -> int:
        return self._display_padding

    def _update_display_width(self) -> None:
        metrics = self.value_display.fontMetrics()
        text = self.value_display.text() or "0"
        desired_width = metrics.horizontalAdvance(text) + 2 * self._display_padding
        self.value_display.setFixedWidth(
            max(self._minimum_display_width, desired_width)
        )

    def value(self) -> int:
        return self._value

    def setValue(self, value: Union[int, float]) -> None:
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            numeric = self._minimum
        normalized = max(self._minimum, numeric)
        if self._maximum is not None:
            normalized = min(normalized, self._maximum)
        if normalized == self._value:
            self._update_state()
            return
        self._value = normalized
        self._update_state()
        self.valueChanged.emit(self._value)

    def _handle_decrease(self) -> None:
        self.setValue(self._value - 1)

    def _handle_increase(self) -> None:
        next_value = self._value + 1
        if self._maximum is not None and next_value > self._maximum:
            next_value = self._maximum
        self.setValue(next_value)

    def _make_button(self, label: str, handler, *, segment: str) -> QPushButton:
        button = QPushButton(label, self)
        button.setCursor(Qt.PointingHandCursor)
        button.setFocusPolicy(Qt.NoFocus)
        diameter = Theme.sizing["entry_height"]
        button.setFixedSize(diameter, diameter)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setStyleSheet(self._button_stylesheet(segment))
        button.clicked.connect(handler)
        return button

    @staticmethod
    def _button_stylesheet(segment: str) -> str:
        disabled_bg = lighten(Theme.colors["secondary"], 0.4)
        disabled_text = lighten(Theme.colors["muted"], 0.2)
        radius_full = Theme.sizing["entry_height"] // 2
        radius_small = max(4, Theme.sizing["entry_height"] // 6)
        outline = Theme.colors["outline"]
        secondary = Theme.colors["secondary"]
        secondary_hover = Theme.colors["secondary_hover"]
        text_color = Theme.colors["text"]

        base = [
            "        QPushButton {",
            f"            background-color: {secondary};",
            f"            color: {text_color};",
            "            padding: 0;",
            f"            border: 1px solid {outline};",
        ]

        if segment == "left":
            base.extend(
                [
                    f"            border-top-left-radius: {radius_full}px;",
                    f"            border-bottom-left-radius: {radius_full}px;",
                    f"            border-top-right-radius: {radius_small}px;",
                    f"            border-bottom-right-radius: {radius_small}px;",
                ]
            )
        else:
            base.extend(
                [
                    f"            border-top-left-radius: {radius_small}px;",
                    f"            border-bottom-left-radius: {radius_small}px;",
                    f"            border-top-right-radius: {radius_full}px;",
                    f"            border-bottom-right-radius: {radius_full}px;",
                ]
            )

        base.append("        }")

        hover = [
            "        QPushButton:hover {",
            f"            background-color: {secondary_hover};",
            "        }",
        ]
        pressed = [
            "        QPushButton:pressed {",
            f"            background-color: {secondary_hover};",
            "        }",
        ]
        disabled = [
            "        QPushButton:disabled {",
            f"            background-color: {disabled_bg};",
            f"            color: {disabled_text};",
            "        }",
        ]

        sections = base + [""] + hover + [""] + pressed + [""] + disabled
        return "\n".join(sections)

    def _update_state(self) -> None:
        self.value_display.setText(str(self._value))
        self._update_display_width()
        self.decrease_button.setEnabled(self._value > self._minimum)
        if self._maximum is not None:
            self.increase_button.setEnabled(self._value < self._maximum)
        else:
            self.increase_button.setEnabled(True)
