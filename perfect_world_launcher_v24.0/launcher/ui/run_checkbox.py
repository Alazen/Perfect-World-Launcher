from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QCheckBox, QSizePolicy, QWidget

from .theme import Theme, lighten


class RunCheckBox(QCheckBox):
    """Accent-styled checkbox used in the Run column."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setText("")
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(40, 32)
        self.setContentsMargins(0, 0, 0, 0)
        self._hovered = False

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(40, 32)

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:  # type: ignore[override]
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:  # type: ignore[override]
        self.update()
        super().focusOutEvent(event)

    def hitButton(self, pos: QPointF) -> bool:  # type: ignore[override]
        return QRectF(self.rect()).contains(pos)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        indicator_size = 24.0
        indicator_rect = QRectF(
            rect.center().x() - indicator_size / 2.0,
            rect.center().y() - indicator_size / 2.0,
            indicator_size,
            indicator_size,
        )
        radius = 8.0

        base_hex = Theme.colors["surface_alt"]
        border_hex = Theme.colors["outline"]
        if self.isChecked():
            base_hex = (
                Theme.colors["accent_hover"]
                if self._hovered or self.isDown()
                else Theme.colors["accent"]
            )
            border_hex = base_hex
        elif self._hovered or self.isDown():
            base_hex = lighten(base_hex, 0.2)
            border_hex = lighten(border_hex, 0.4)

        fill_color = QColor(base_hex)
        outline_color = QColor(border_hex)

        if not self.isEnabled():
            fill_color = fill_color.darker(130)
            outline_color = outline_color.darker(130)

        border_pen = QPen(outline_color, 2.0)
        border_pen.setCosmetic(True)
        painter.setPen(border_pen)
        painter.setBrush(fill_color)
        painter.drawRoundedRect(indicator_rect, radius, radius)

        if self.hasFocus():
            focus_pen = QPen(QColor(Theme.colors["accent"]), 1.5, Qt.DashLine)
            focus_pen.setCosmetic(True)
            painter.setPen(focus_pen)
            painter.setBrush(Qt.NoBrush)
            focus_rect = indicator_rect.adjusted(-4.0, -4.0, 4.0, 4.0)
            painter.drawRoundedRect(focus_rect, radius + 4.0, radius + 4.0)

        if self.isChecked():
            painter.setBrush(Qt.NoBrush)
            check_pen = QPen(QColor(Theme.colors["accent_text"]), 2.8)
            check_pen.setCapStyle(Qt.RoundCap)
            check_pen.setJoinStyle(Qt.RoundJoin)
            check_pen.setCosmetic(True)
            painter.setPen(check_pen)
            p1 = QPointF(
                indicator_rect.left() + indicator_rect.width() * 0.25,
                indicator_rect.center().y() + indicator_rect.height() * 0.1,
            )
            p2 = QPointF(
                indicator_rect.center().x() - indicator_rect.width() * 0.05,
                indicator_rect.bottom() - indicator_rect.height() * 0.22,
            )
            p3 = QPointF(
                indicator_rect.right() - indicator_rect.width() * 0.18,
                indicator_rect.top() + indicator_rect.height() * 0.25,
            )
            painter.drawLine(p1, p2)
            painter.drawLine(p2, p3)
