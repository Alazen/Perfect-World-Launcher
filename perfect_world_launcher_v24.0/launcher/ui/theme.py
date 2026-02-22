from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QPushButton, QSizePolicy


def lighten(color_hex: str, factor: float = 0.25) -> str:
    color = QColor(color_hex)
    return color.lighter(max(1, int(100 + factor * 100))).name()


class Theme:
    colors: Dict[str, str] = {
        "bg": "#121417",
        "surface": "#1a1d21",
        "surface_alt": "#20242a",
        "outline": "#2b3139",
        "secondary": "#2f353d",
        "secondary_hover": "#3a414b",
        "muted": "#b8c0cc",
        "text": "#f1f2f5",
        "accent": "#38bdf8",
        "accent_hover": "#0ea5e9",
        "accent_text": "#041019",
        "danger": "#fb7185",
        "danger_hover": "#fda4af",
        "log_bg": "#14181d",
        "log_text": "#f8fafc",
    }
    sizing: Dict[str, int] = {
        "card_radius": 24,
        "inner_radius": 20,
        "button_height": 38,
        "entry_height": 38,
        "section_padding": 24,
    }
    sizing["pill_radius"] = max(sizing["button_height"], sizing["entry_height"]) // 2
    button_primary: Dict[str, object] = {
        "fg_color": colors["accent"],
        "hover_color": colors["accent_hover"],
        "corner_radius": sizing["pill_radius"],
        "height": sizing["button_height"],
        "text_color": colors["accent_text"],
    }
    button_secondary: Dict[str, object] = {
        "fg_color": colors["secondary"],
        "hover_color": colors["secondary_hover"],
        "corner_radius": sizing["pill_radius"],
        "height": sizing["button_height"],
        "text_color": colors["text"],
        "border_width": 1,
        "border_color": colors["outline"],
    }
    button_danger: Dict[str, object] = {
        "fg_color": colors["danger"],
        "hover_color": colors["danger_hover"],
        "corner_radius": sizing["pill_radius"],
        "height": sizing["button_height"],
        "text_color": colors["text"],
    }
    entry_style: Dict[str, object] = {
        "fg_color": colors["surface_alt"],
        "border_color": colors["outline"],
        "text_color": colors["text"],
        "corner_radius": sizing["pill_radius"],
        "border_width": 1,
        "height": sizing["entry_height"],
    }


_BUTTON_STYLE_CACHE: Dict[int, str] = {}
_LINE_EDIT_STYLESHEET: Optional[str] = None
_PLAIN_TEXT_STYLESHEET: Optional[str] = None


def apply_button_style(button: QPushButton, style: Dict[str, object]) -> None:
    button.setCursor(Qt.PointingHandCursor)
    button.setFixedHeight(style["height"])
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    button.setStyleSheet(_button_stylesheet(style))


def _button_stylesheet(style: Dict[str, object]) -> str:
    key = id(style)
    cached = _BUTTON_STYLE_CACHE.get(key)
    if cached is None:
        border_width = int(style.get("border_width", 0))
        border_color = str(style.get("border_color", "transparent"))
        disabled_bg = lighten(str(style["fg_color"]), 0.35)
        disabled_text = lighten(str(style["text_color"]), 0.35)
        cached = f"""
        QPushButton {{
            background-color: {style["fg_color"]};
            border-radius: {style["corner_radius"]}px;
            color: {style["text_color"]};
            border: {border_width}px solid {border_color};
            padding: 8px 18px;
        }}
        QPushButton:hover {{
            background-color: {style["hover_color"]};
            border-radius: {style["corner_radius"]}px;
        }}
        QPushButton:pressed {{
            background-color: {style["hover_color"]};
            border-radius: {style["corner_radius"]}px;
        }}
        QPushButton:disabled {{
            background-color: {disabled_bg};
            color: {disabled_text};
            border: {border_width}px solid {border_color};
            border-radius: {style["corner_radius"]}px;
        }}
        """
        _BUTTON_STYLE_CACHE[key] = cached
    return cached


def apply_line_edit_style(line_edit: QLineEdit) -> None:
    line_edit.setFixedHeight(Theme.entry_style["height"])
    line_edit.setStyleSheet(_line_edit_stylesheet())


def _line_edit_stylesheet() -> str:
    global _LINE_EDIT_STYLESHEET
    if _LINE_EDIT_STYLESHEET is None:
        style = Theme.entry_style
        _LINE_EDIT_STYLESHEET = f"""
        QLineEdit {{
            background-color: {style["fg_color"]};
            border-radius: {style["corner_radius"]}px;
            color: {style["text_color"]};
            border: {style["border_width"]}px solid {style["border_color"]};
            padding: 0 14px;
        }}
        QLineEdit:focus {{
            border-color: {Theme.colors["accent"]};
            border-radius: {style["corner_radius"]}px;
        }}
        QLineEdit[invalid="true"] {{
            border-color: {Theme.colors["danger"]};
            border-radius: {style["corner_radius"]}px;
        }}
        """
    return _LINE_EDIT_STYLESHEET


def apply_plain_text_style(textbox: QPlainTextEdit) -> None:
    textbox.setReadOnly(True)
    textbox.setMaximumBlockCount(1000)
    textbox.setStyleSheet(_plain_text_stylesheet())


def _plain_text_stylesheet() -> str:
    global _PLAIN_TEXT_STYLESHEET
    if _PLAIN_TEXT_STYLESHEET is None:
        _PLAIN_TEXT_STYLESHEET = f"""
        QPlainTextEdit {{
            background-color: {Theme.colors["log_bg"]};
            border-radius: {Theme.sizing["inner_radius"]}px;
            border: 0px;
            color: {Theme.colors["log_text"]};
            padding: 16px;
        }}
        """
    return _PLAIN_TEXT_STYLESHEET
