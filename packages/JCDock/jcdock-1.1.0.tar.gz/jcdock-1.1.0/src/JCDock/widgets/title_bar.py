# title_bar.py

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QStyle, QApplication, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPoint, QRect, QEvent, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush, QMouseEvent, QPainterPath, QPalette, QRegion, QPen, QIcon, QPixmap
from typing import Union, Optional

from ..core.docking_state import DockingState
from ..utils.icon_cache import IconCache


class TitleBar(QWidget):
    def __init__(self, title, parent=None, top_level_widget=None, title_text_color=None, icon: Optional[Union[str, QIcon]] = None):
        super().__init__(parent)
        self._top_level_widget = top_level_widget if top_level_widget is not None else parent
        self.setObjectName(f"TitleBar_{title.replace(' ', '_')}")
        self.setAutoFillBackground(False)
        self.setFixedHeight(42)
        self.setMouseTracking(True)

        if title_text_color is not None:
            self._title_text_color = title_text_color
        else:
            self._title_text_color = QColor("#101010")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        # Create icon label (optional)
        self.icon_label = None
        if icon is not None:
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(24, 24)
            self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.set_icon(icon)
            layout.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"background: transparent; color: {self._title_text_color.name()};")
        self.title_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout.addWidget(self.title_label, 1)

        button_style = """
            QPushButton { background-color: transparent; border: none; }
            QPushButton:hover { background-color: #D0D0D0; border-radius: 4px; }
            QPushButton:pressed { background-color: #B8B8B8; }
        """

        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(self._create_control_icon("minimize"))
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setStyleSheet(button_style)
        self.minimize_button.clicked.connect(self._top_level_widget.showMinimized)
        layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(self._create_control_icon("maximize"))
        self.maximize_button.setFixedSize(24, 24)
        self.maximize_button.setStyleSheet(button_style)
        if hasattr(self._top_level_widget, 'toggle_maximize'):
            self.maximize_button.clicked.connect(self._top_level_widget.toggle_maximize)
        layout.addWidget(self.maximize_button)

        self.close_button = QPushButton()
        self.close_button.setIcon(self._create_control_icon("close"))
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(button_style)

        self.close_button.clicked.connect(self.on_close_button_clicked)

        layout.addWidget(self.close_button)

        self.moving = False
        self.offset = QPoint()

    def get_title_text_color(self):
        """Get the current title text color."""
        return self._title_text_color

    def set_title_text_color(self, color):
        """Set the title text color and update the label stylesheet."""
        if isinstance(color, QColor):
            self._title_text_color = color
        else:
            self._title_text_color = QColor(color)
        self.title_label.setStyleSheet(f"background: transparent; color: {self._title_text_color.name()};")

    def set_icon(self, icon: Optional[Union[str, QIcon]]):
        """
        Set or update the title bar icon.
        
        Args:
            icon: Icon source - can be file path, Unicode character, Qt standard icon name, or QIcon object
        """
        if self.icon_label is None:
            # Create icon label if it doesn't exist
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(24, 24)
            self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.icon_label.setAlignment(Qt.AlignCenter)
            # Insert before title label (should be at index 0)
            self.layout().insertWidget(0, self.icon_label)
        
        if icon is None:
            # Remove icon
            self.icon_label.clear()
            self.icon_label.hide()
            return
        
        # Get icon using the icon cache
        qicon = IconCache.get_custom_icon(icon, 24, self._title_text_color.name())
        if qicon is not None:
            pixmap = qicon.pixmap(24, 24)
            self.icon_label.setPixmap(pixmap)
            self.icon_label.show()
        else:
            # Failed to load icon - hide the icon label
            self.icon_label.clear()
            self.icon_label.hide()

    def get_icon(self) -> Optional[QIcon]:
        """Get the current icon as a QIcon object."""
        if self.icon_label and not self.icon_label.pixmap().isNull():
            return QIcon(self.icon_label.pixmap())
        return None

    def has_icon(self) -> bool:
        """Check if the title bar currently has an icon."""
        return self.icon_label is not None and not self.icon_label.pixmap().isNull()

    def paintEvent(self, event):
        """Paint the title bar background with rounded top corners and border edges."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor("#F0F0F0")
        if hasattr(self._top_level_widget, '_title_bar_color'):
            bg_color = self._top_level_widget._title_bar_color
        
        rect = QRectF(self.rect())
        path = QPainterPath()
        radius = 8.0
        
        path.moveTo(rect.left(), rect.bottom())
        path.lineTo(rect.left(), rect.top() + radius)
        path.arcTo(rect.left(), rect.top(), radius * 2, radius * 2, 180, -90)
        path.lineTo(rect.right() - radius, rect.top())
        path.arcTo(rect.right() - radius * 2, rect.top(), radius * 2, radius * 2, 90, -90)
        path.lineTo(rect.right(), rect.bottom())
        path.closeSubpath()
        
        painter.fillPath(path, QBrush(bg_color))
        
        # Draw border around title bar edges (top, left, right)
        border_color = QColor("#6A8EAE")
        pen = QPen(border_color, 1.0)
        painter.setPen(pen)
        
        # Create border path that follows the same rounded corners
        border_path = QPainterPath()
        border_path.moveTo(rect.left(), rect.bottom())
        border_path.lineTo(rect.left(), rect.top() + radius)
        border_path.arcTo(rect.left(), rect.top(), radius * 2, radius * 2, 180, -90)
        border_path.lineTo(rect.right() - radius, rect.top())
        border_path.arcTo(rect.right() - radius * 2, rect.top(), radius * 2, radius * 2, 90, -90)
        border_path.lineTo(rect.right(), rect.bottom())
        
        painter.drawPath(border_path)
        super().paintEvent(event)

    def on_close_button_clicked(self):
        """Determines whether to close a single widget or a whole container."""
        from .dock_container import DockContainer

        manager = getattr(self._top_level_widget, 'manager', None)
        if not manager:
            self._top_level_widget.close()
            return

        if isinstance(self._top_level_widget, DockContainer):
            manager.request_close_container(self._top_level_widget)
        else:
            manager.request_close_widget(self._top_level_widget)

    def mouseMoveEvent(self, event):
        if self.moving:
            if hasattr(self._top_level_widget, 'manager') and self._top_level_widget.manager:
                self._top_level_widget.manager.handle_live_move(self._top_level_widget, event)
            new_widget_global = event.globalPosition().toPoint() - self.offset
            self._top_level_widget.move(new_widget_global)
            return
        
        # Update resize cursor when hovering over title bar edges
        from .dock_container import DockContainer
        if isinstance(self._top_level_widget, DockContainer) and not getattr(self._top_level_widget, '_is_maximized', False):
            pos = event.pos()
            margin = getattr(self._top_level_widget, 'resize_margin', 8)
            on_left = 0 <= pos.x() < margin
            on_right = self.width() - margin < pos.x() <= self.width()
            on_top = 0 <= pos.y() < margin

            edge = None
            if on_top:
                if on_left:
                    edge = "top_left"
                elif on_right:
                    edge = "top_right"
                else:
                    edge = "top"
            elif on_left:
                edge = "left"
            elif on_right:
                edge = "right"

            # Update cursor based on edge
            if edge:
                if edge in ["top", "bottom"]:
                    self.setCursor(Qt.SizeVerCursor)
                elif edge in ["left", "right"]:
                    self.setCursor(Qt.SizeHorCursor)
                elif edge in ["top_left", "bottom_right"]:
                    self.setCursor(Qt.SizeFDiagCursor)
                elif edge in ["top_right", "bottom_left"]:
                    self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.unsetCursor()
        else:
            self.unsetCursor()
            
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if (self.close_button.geometry().contains(event.pos()) or
                self.maximize_button.geometry().contains(event.pos()) or
                self.minimize_button.geometry().contains(event.pos())):
            super().mousePressEvent(event)
            return

        if event.button() == Qt.LeftButton:
            from .dock_container import DockContainer
            
            edge = None
            if isinstance(self._top_level_widget, DockContainer):
                pos = event.pos()
                margin = getattr(self._top_level_widget, 'resize_margin', 8)
                on_left = 0 <= pos.x() < margin
                on_right = self.width() - margin < pos.x() <= self.width()
                on_top = 0 <= pos.y() < margin

                if on_top:
                    if on_left:
                        edge = "top_left"
                    elif on_right:
                        edge = "top_right"
                    else:
                        edge = "top"
                elif on_left:
                    edge = "left"
                elif on_right:
                    edge = "right"

                if edge:
                    # Use centralized resize initiation from DockContainer
                    if hasattr(self._top_level_widget, 'initiate_resize'):
                        self._top_level_widget.initiate_resize(edge, event.globalPosition().toPoint())

            if not edge:
                if hasattr(self._top_level_widget, 'on_activation_request'):
                    self._top_level_widget.on_activation_request()
                if hasattr(self._top_level_widget, 'manager') and self._top_level_widget.manager:
                    if hasattr(self._top_level_widget.manager, 'destroy_all_overlays'):
                        self._top_level_widget.manager.destroy_all_overlays()

                self.moving = True
                self.offset = event.globalPosition().toPoint() - self._top_level_widget.pos()
                
                if hasattr(self._top_level_widget, 'manager') and self._top_level_widget.manager:
                    manager = self._top_level_widget.manager
                    manager.hit_test_cache.build_cache(manager.window_stack, manager.containers)
                    manager._set_state(DockingState.DRAGGING_WINDOW)
                    manager.hit_test_cache.set_drag_operation_state(True, self._top_level_widget)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.moving:
                # First, clear the moving flag
                self.moving = False
                
                manager = getattr(self._top_level_widget, 'manager', None)
                if manager and hasattr(manager, 'last_dock_target') and manager.last_dock_target:
                    manager.finalize_dock_from_live_move(self._top_level_widget, manager.last_dock_target)
                
                if manager:
                    # Clean up drag proxy if no dock target
                    if not (hasattr(manager, 'last_dock_target') and manager.last_dock_target):
                        if hasattr(manager, 'drag_drop_controller') and manager.drag_drop_controller._drag_proxy:
                            manager.drag_drop_controller._cleanup_drag_proxy()
                            self._top_level_widget.setWindowOpacity(1.0)  # Restore visibility
                    
                    if hasattr(manager, 'last_dock_target'):
                        manager.last_dock_target = None
                    if hasattr(manager, 'destroy_all_overlays'):
                        manager.destroy_all_overlays()
                    if hasattr(manager, 'hit_test_cache'):
                        manager.hit_test_cache.set_drag_operation_state(False)
                    manager._set_state(DockingState.IDLE)
                
                if hasattr(self._top_level_widget, 'restore_normal_opacity'):
                    self._top_level_widget.restore_normal_opacity()
            if hasattr(self._top_level_widget, 'resizing') and self._top_level_widget.resizing:
                # Use centralized resize finishing from DockContainer
                if hasattr(self._top_level_widget, '_finish_resize'):
                    self._top_level_widget._finish_resize()

    def _create_control_icon(self, icon_type: str, color=QColor("#303030")):
        """Creates cached window control icons for improved performance."""
        return IconCache.get_control_icon(icon_type, color.name(), 24)