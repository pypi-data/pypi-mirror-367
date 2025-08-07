"""
UI management functionality for the JCDock test suite.
Handles menu creation, widget factories, and UI interactions.
"""

import random
from datetime import datetime
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, 
    QPushButton, QTextEdit, QListWidget, QMenuBar
)
from PySide6.QtCore import QSize, QPoint, QTimer
from PySide6.QtGui import QColor

from JCDock.core.widget_registry import get_registry
from JCDock.widgets.dock_container import DockContainer
from ..widgets.test_widgets import TestContentWidget, TabWidget1, TabWidget2, RightWidget
from ..widgets.financial_widgets import ChartWidget, OrderWidget, PortfolioWidget
from ..utils.constants import (
    DEFAULT_WINDOW_SIZE, CASCADE_OFFSET, DEFAULT_POSITION,
    UNICODE_ICONS, QT_STANDARD_ICONS, DYNAMIC_ICONS, Colors,
    DYNAMIC_ITEMS_COUNT, TEST_DELAY_MS
)


class UIManager:
    """Manages UI elements, menus, and widget creation."""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.docking_manager = main_app.docking_manager
        self.main_window = main_app.main_window
        self.widget_count = 0
    
    def create_test_menu_bar(self):
        """Create the menu bar for the main window with various test actions."""
        menu_bar = self.main_window.menuBar()

        self._create_file_menu(menu_bar)
        self._create_widget_menu(menu_bar)
        self._create_test_menu(menu_bar)
        self._create_color_menu(menu_bar)
        self._create_icon_menu(menu_bar)
    
    def _create_file_menu(self, menu_bar: QMenuBar):
        """Create the File menu."""
        file_menu = menu_bar.addMenu("File")
        
        save_layout_action = file_menu.addAction("Save Layout")
        save_layout_action.triggered.connect(self.main_app.layout_manager.save_layout)
        
        load_layout_action = file_menu.addAction("Load Layout")
        load_layout_action.triggered.connect(self.main_app.layout_manager.load_layout)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.main_window.close)
    
    def _create_widget_menu(self, menu_bar: QMenuBar):
        """Create the Widgets menu."""
        widget_menu = menu_bar.addMenu("Widgets")
        
        # Test Widgets submenu
        test_widgets_menu = widget_menu.addMenu("Create Test Widgets")
        self._add_test_widget_actions(test_widgets_menu)
        
        widget_menu.addSeparator()
        
        # Ad-Hoc State Handlers submenu
        adhoc_menu = widget_menu.addMenu("Create with Ad-Hoc State Handlers")
        adhoc_stateful_action = adhoc_menu.addAction("Stateful Widget with Ad-Hoc Handlers")
        adhoc_stateful_action.triggered.connect(self._create_widget_with_adhoc_handlers)
        
        widget_menu.addSeparator()
        
        create_layout_window_action = widget_menu.addAction("Create Layout Window")
        create_layout_window_action.triggered.connect(self._create_layout_window)
    
    def _add_test_widget_actions(self, menu):
        """Add test widget actions to menu."""
        widget_types = [
            ("test_widget", "Test Widget (State Persistence)"),
            ("tooltip_widget", "Tooltip Widget"),
            ("context_menu_widget", "Context Menu Widget"),
            ("form_widget", "Form Widget"),
            ("complex_layout_widget", "Complex Layout Widget")
        ]
        
        for widget_key, display_name in widget_types:
            action = menu.addAction(display_name)
            action.triggered.connect(lambda checked, key=widget_key: self._create_test_widget(key))
    
    
    def _create_test_menu(self, menu_bar: QMenuBar):
        """Create the Tests menu."""
        test_menu = menu_bar.addMenu("Tests")
        
        test_actions = [
            ("Test: Find Widget by ID", self.main_app.test_manager.run_find_widget_test),
            ("Test: List All Widgets", self.main_app.test_manager.run_list_all_widgets_test),
            ("Test: List Floating Widgets", self.main_app.test_manager.run_get_floating_widgets_test),
            ("Test: Is Widget Docked?", self.main_app.test_manager.run_is_widget_docked_test),
            ("Test: Programmatic Dock", self.main_app.test_manager.run_programmatic_dock_test),
            ("Test: Programmatic Undock", self.main_app.test_manager.run_programmatic_undock_test),
            ("Test: Programmatic Move to Main", self.main_app.test_manager.run_programmatic_move_test),
            ("Test: Activate Widget", self.main_app.test_manager.run_activate_widget_test)
        ]
        
        for action_text, action_func in test_actions:
            action = test_menu.addAction(action_text)
            action.triggered.connect(action_func)
        
        test_menu.addSeparator()
        
        self.debug_mode_action = test_menu.addAction("Toggle Debug Mode")
        self.debug_mode_action.setCheckable(True)
        self.debug_mode_action.setChecked(self.docking_manager.debug_mode)
        self.debug_mode_action.triggered.connect(self.docking_manager.set_debug_mode)
        
        test_menu.addSeparator()
        
        run_all_tests_action = test_menu.addAction("Run All Tests Sequentially")
        run_all_tests_action.triggered.connect(self.main_app.test_manager.run_all_tests_sequentially)
    
    def _create_color_menu(self, menu_bar: QMenuBar):
        """Create the Colors menu."""
        color_menu = menu_bar.addMenu("Colors")
        
        # Container colors submenu
        container_colors_menu = color_menu.addMenu("Container Colors")
        container_bg_action = container_colors_menu.addAction("Set Container Background to Light Blue")
        container_bg_action.triggered.connect(lambda: self._set_container_background_color(Colors.LIGHT_BLUE))
        
        container_border_action = container_colors_menu.addAction("Set Container Border to Dark Blue")
        container_border_action.triggered.connect(lambda: self._set_container_border_color(Colors.DARK_BLUE))
        
        # Floating window colors submenu
        floating_colors_menu = color_menu.addMenu("Floating Window Colors")
        floating_bg_action = floating_colors_menu.addAction("Create Floating Window - Green Theme")
        floating_bg_action.triggered.connect(
            lambda: self._create_colored_floating_window(Colors.FOREST_GREEN, QColor("#FFFFFF"))
        )
        
        floating_bg2_action = floating_colors_menu.addAction("Create Floating Window - Purple Theme")
        floating_bg2_action.triggered.connect(
            lambda: self._create_colored_floating_window(Colors.SLATE_BLUE, QColor("#FFFFFF"))
        )
        
        floating_bg3_action = floating_colors_menu.addAction("Create Floating Window - Dark Theme")
        floating_bg3_action.triggered.connect(
            lambda: self._create_colored_floating_window(Colors.DARK_GRAY, Colors.BRIGHT_GREEN)
        )
        
        # Title bar text color submenu
        title_text_menu = color_menu.addMenu("Title Bar Text Colors")
        title_colors = [
            ("Change Main Window Title Text to Red", Colors.RED),
            ("Change Main Window Title Text to Blue", Colors.BLUE),
            ("Change Main Window Title Text to Gold", Colors.GOLD)
        ]
        
        for action_text, color in title_colors:
            action = title_text_menu.addAction(action_text)
            action.triggered.connect(lambda checked, c=color: self._change_main_window_title_text_color(c))
        
        # Reset colors
        color_menu.addSeparator()
        reset_colors_action = color_menu.addAction("Reset All Colors to Defaults")
        reset_colors_action.triggered.connect(self._reset_all_colors)
    
    def _create_icon_menu(self, menu_bar: QMenuBar):
        """Create the Icons menu."""
        icon_menu = menu_bar.addMenu("Icons")
        
        # Unicode emoji icons submenu
        unicode_icons_menu = icon_menu.addMenu("Unicode Emoji Icons")
        unicode_examples = [
            ("Create Window with House Icon", "🏠", "Home"),
            ("Create Window with Gear Icon", "⚙️", "Settings"),
            ("Create Window with Chart Icon", "📊", "Analytics"),
            ("Create Window with Rocket Icon", "🚀", "Launch")
        ]
        
        for action_text, icon, title_suffix in unicode_examples:
            action = unicode_icons_menu.addAction(action_text)
            action.triggered.connect(lambda checked, i=icon, t=title_suffix: self._create_window_with_unicode_icon(i, t))
        
        # Qt Standard icons submenu
        qt_icons_menu = icon_menu.addMenu("Qt Standard Icons")
        qt_examples = [
            ("Create Window with File Icon", "SP_FileIcon", "Files"),
            ("Create Window with Folder Icon", "SP_DirIcon", "Folders"),
            ("Create Window with Computer Icon", "SP_ComputerIcon", "Computer")
        ]
        
        for action_text, icon_name, title_suffix in qt_examples:
            action = qt_icons_menu.addAction(action_text)
            action.triggered.connect(lambda checked, i=icon_name, t=title_suffix: self._create_window_with_qt_icon(i, t))
        
        # No icon test
        icon_menu.addSeparator()
        no_icon_action = icon_menu.addAction("Create Window with No Icon")
        no_icon_action.triggered.connect(self._create_window_with_no_icon)
        
        # Dynamic icon change tests
        icon_menu.addSeparator()
        dynamic_menu = icon_menu.addMenu("Dynamic Icon Changes")
        
        change_main_icon_action = dynamic_menu.addAction("Add Icon to Main Window")
        change_main_icon_action.triggered.connect(self._add_icon_to_main_window)
        
        remove_main_icon_action = dynamic_menu.addAction("Remove Icon from Main Window")
        remove_main_icon_action.triggered.connect(self._remove_icon_from_main_window)
        
        change_container_icon_action = dynamic_menu.addAction("Change Icon of First Container")
        change_container_icon_action.triggered.connect(self._change_first_container_icon)
        
        change_widget_icon_action = dynamic_menu.addAction("Change Icon of First Widget")
        change_widget_icon_action.triggered.connect(self._change_first_widget_icon)
    
    # Widget creation methods
    def _create_test_widget(self, widget_key: str):
        """Create a test widget using the unified API."""
        print(f"Creating test widget: {widget_key}")
        
        count = len(self.docking_manager.widgets)
        x = DEFAULT_POSITION.x() + count * CASCADE_OFFSET
        y = DEFAULT_POSITION.y() + count * CASCADE_OFFSET
        
        widget_instance = self._create_widget_instance(widget_key)
        if not widget_instance:
            return
            
        # Create descriptive titles based on widget purpose
        title_map = {
            "test_widget": "Test Widget (State Persistence)",
            "tooltip_widget": "Tooltip Widget", 
            "context_menu_widget": "Context Menu Widget",
            "form_widget": "Form Widget",
            "complex_layout_widget": "Complex Layout Widget"
        }
        
        title = title_map.get(widget_key, widget_key.replace('_', ' ').title())
        
        container = self.docking_manager.create_window(
            widget_instance,
            key=widget_key,
            title=title,
            x=x, y=y,
            width=DEFAULT_WINDOW_SIZE.width(),
            height=DEFAULT_WINDOW_SIZE.height(),
            persist=True
        )
        
        print(f"Created test widget container: {container}")
    
    def _create_widget_instance(self, widget_key: str) -> QWidget:
        """Create a widget instance based on the key."""
        widget_map = {
            "test_widget": lambda: TestContentWidget("Test Widget"),
            "tooltip_widget": TabWidget1,
            "context_menu_widget": TabWidget2,
            "form_widget": OrderWidget,
            "complex_layout_widget": PortfolioWidget
        }
        
        if widget_key in widget_map:
            return widget_map[widget_key]()
        else:
            print(f"Unknown widget key: {widget_key}")
            return None
    
    
    
    def _create_widget_with_adhoc_handlers(self):
        """Create a widget using ad-hoc state handlers for persistence."""
        print("Creating widget with ad-hoc state handlers...")
        
        widget_instance = self._create_adhoc_stateful_widget()
        
        # Modify its state to demonstrate persistence
        widget_instance.text_input.setText("This will be preserved!")
        widget_instance.counter_spin.setValue(789)
        widget_instance._simulate_clicks(5)
        
        count = len(self.docking_manager.widgets)
        x = DEFAULT_POSITION.x() + 200 + count * CASCADE_OFFSET
        y = DEFAULT_POSITION.y() + 200 + count * CASCADE_OFFSET
        
        container = self.docking_manager.create_window(
            widget_instance,
            key="adhoc_stateful_widget",
            title="Widget with Ad-Hoc State Handlers",
            x=x, y=y,
            width=450, height=350,
            persist=True
        )
        
        # TODO: State handlers not yet supported in create_window()
        # state_provider=self._extract_adhoc_widget_state,
        # state_restorer=self._restore_adhoc_widget_state
        
        print(f"Created widget with ad-hoc state handlers: {container}")
    
    def _create_adhoc_stateful_widget(self) -> QWidget:
        """Create a widget that doesn't have built-in state persistence methods."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel("Ad-Hoc State Handler Demo")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #e8f4fd; border-radius: 5px;")
        layout.addWidget(header)
        
        explanation = QLabel("This widget doesn't have get_dock_state/set_dock_state methods.\nState is managed through external handler functions.")
        explanation.setStyleSheet("font-style: italic; color: #666; padding: 5px;")
        layout.addWidget(explanation)
        
        layout.addWidget(QLabel("Text Input (will be preserved):"))
        widget.text_input = QLineEdit()
        widget.text_input.setPlaceholderText("Enter text to be preserved across sessions...")
        layout.addWidget(widget.text_input)
        
        layout.addWidget(QLabel("Counter (will be preserved):"))
        widget.counter_spin = QSpinBox()
        widget.counter_spin.setRange(0, 9999)
        widget.counter_spin.setValue(0)
        layout.addWidget(widget.counter_spin)
        
        widget.click_count = 0
        widget.click_button = QPushButton("Click Me (count preserved)")
        widget.click_button.clicked.connect(lambda: widget._on_click())
        layout.addWidget(widget.click_button)
        
        widget.status_label = QLabel("Clicks: 0 (NEW WIDGET)")
        layout.addWidget(widget.status_label)
        
        layout.addWidget(QLabel("Notes (will be preserved):"))
        widget.notes_area = QTextEdit()
        widget.notes_area.setPlaceholderText("Add some notes that will persist...")
        widget.notes_area.setMaximumHeight(100)
        layout.addWidget(widget.notes_area)
        
        # Add methods to the widget instance
        def on_click():
            widget.click_count += 1
            widget.status_label.setText(f"Clicks: {widget.click_count} (MANUAL)")
        
        def simulate_clicks(count):
            for _ in range(count):
                on_click()
        
        widget._on_click = on_click
        widget._simulate_clicks = simulate_clicks
        
        return widget
    
    def _extract_adhoc_widget_state(self, widget) -> Dict[str, Any]:
        """Ad-hoc state provider function - extracts state from the widget."""
        return {
            'text_input_value': widget.text_input.text(),
            'counter_value': widget.counter_spin.value(), 
            'click_count': widget.click_count,
            'notes_content': widget.notes_area.toPlainText()
        }
    
    def _restore_adhoc_widget_state(self, widget, state_dict: Dict[str, Any]):
        """Ad-hoc state restorer function - restores state to the widget."""
        if not isinstance(state_dict, dict):
            widget.status_label.setText("Clicks: 0 (RESTORE FAILED - Invalid data)")
            return
        
        try:
            text_value = state_dict.get('text_input_value', '')
            counter_value = state_dict.get('counter_value', 0)
            notes_value = state_dict.get('notes_content', '')
            click_count = state_dict.get('click_count', 0)
            
            widget.text_input.setText(text_value)
            widget.counter_spin.setValue(counter_value)
            widget.notes_area.setPlainText(notes_value)
            
            widget.click_count = click_count
            widget.status_label.setText(f"Clicks: {widget.click_count} (RESTORED ✓)")
            
        except Exception as e:
            widget.status_label.setText(f"Clicks: 0 (RESTORE FAILED - {str(e)})")
    

    def _create_layout_window(self):
        """Create a new layout window (persistent container for docking widgets)."""
        container = self.docking_manager.create_window(
            content=None,
            title="Layout Window",
            x=400, y=300, width=600, height=500,
            auto_persistent_root=True,
            preserve_title=True
        )
        print(f"Created layout window: {container}")
    
    # Color management methods
    def _set_container_background_color(self, color: QColor):
        """Set background color for the main container."""
        self.main_window.set_background_color(color)
        print(f"Set main container background color to {color.name()}")
    
    def _set_container_border_color(self, color: QColor):
        """Set border color for the main container."""
        self.main_window.set_border_color(color)
        print(f"Set main container border color to {color.name()}")
    
    def _create_colored_floating_window(self, title_bar_color: QColor, title_text_color: QColor):
        """Create a new floating window with custom colors."""
        floating_root = self.docking_manager.create_window(
            is_main_window=False,
            title="Custom Colored Window",
            x=100, y=100, width=400, height=300,
            title_bar_color=title_bar_color,
            title_text_color=title_text_color,
            auto_persistent_root=True
        )
        floating_root.show()
        print(f"Created floating window with title bar color {title_bar_color.name()} and text color {title_text_color.name()}")
    
    def _change_main_window_title_text_color(self, color: QColor):
        """Change the title bar text color of the main window."""
        if self.main_window.title_bar:
            self.main_window.set_title_text_color(color)
            print(f"Changed main window title text color to {color.name()}")
        else:
            print("Main window has no title bar to change text color")
    
    def _reset_all_colors(self):
        """Reset all colors to their defaults."""
        self.main_window.set_background_color(Colors.DEFAULT_BACKGROUND)
        self.main_window.set_border_color(Colors.DEFAULT_BORDER)
        if self.main_window.title_bar:
            self.main_window.set_title_text_color(Colors.DEFAULT_TITLE_TEXT)
        print("Reset all colors to defaults")
    
    # Icon management methods
    def _create_window_with_unicode_icon(self, icon: str, title_suffix: str):
        """Create a dockable widget with a Unicode emoji icon."""
        from ..widgets.test_widgets import TestContentWidget
        
        # Create content widget
        content_widget = TestContentWidget(f"{title_suffix} Content")
        
        # Create dockable widget container
        container = self.docking_manager.create_window(
            content_widget,
            title=f"{title_suffix} Window",
            x=200, y=200, width=400, height=300,
            icon=icon
        )
        print(f"Created dockable widget '{title_suffix} Window' with Unicode icon")
    
    def _create_window_with_qt_icon(self, icon_name: str, title_suffix: str):
        """Create a dockable widget with a Qt Standard icon."""
        from ..widgets.test_widgets import TestContentWidget
        
        # Create content widget
        content_widget = TestContentWidget(f"{title_suffix} Content")
        
        # Create dockable widget container
        container = self.docking_manager.create_window(
            content_widget,
            title=f"{title_suffix} Window",
            x=250, y=250, width=400, height=300,
            icon=icon_name
        )
        print(f"Created dockable widget '{title_suffix} Window' with Qt standard icon")
    
    def _create_window_with_no_icon(self):
        """Create a dockable widget with no icon to test fallback behavior."""
        from ..widgets.test_widgets import TestContentWidget
        
        # Create content widget
        content_widget = TestContentWidget("No Icon Content")
        
        # Create dockable widget container
        container = self.docking_manager.create_window(
            content_widget,
            title="No Icon Window",
            x=300, y=300, width=400, height=300
        )
        
        # Explicitly do not set an icon
        print("Created dockable widget with no icon (fallback test)")
    
    def _add_icon_to_main_window(self):
        """Add an icon to the main window's title bar."""
        if self.main_window.title_bar:
            self.main_window.set_icon("🏠")
            print("Added house icon to main window")
        else:
            print("Main window has no title bar")
    
    def _remove_icon_from_main_window(self):
        """Remove the icon from the main window's title bar."""
        if self.main_window.title_bar:
            self.main_window.set_icon(None)
            print("Removed icon from main window")
        else:
            print("Main window has no title bar")
    
    def _change_first_container_icon(self):
        """Change the icon of the first available container."""
        target_container = None
        for container in self.docking_manager.containers:
            if container != self.main_window and container.title_bar:
                target_container = container
                break
        
        if target_container:
            next_icon = random.choice(DYNAMIC_ICONS)
            target_container.set_icon(next_icon)
            print(f"Changed icon of container '{target_container.windowTitle()}'")
        else:
            print("No suitable container found (need a floating window with title bar)")
            print("Try creating a floating window first using the 'Widgets' menu")

    def _change_first_widget_icon(self):
        """Change the icon of the first available widget."""
        all_widgets = self.docking_manager.get_all_widgets()
        if not all_widgets:
            print("No widgets available to change icon")
            return
            
        from ..utils.constants import DYNAMIC_ICONS
        import random
        
        target_widget = all_widgets[0]
        if hasattr(target_widget, 'set_icon'):
            next_icon = random.choice(DYNAMIC_ICONS)
            target_widget.set_icon(next_icon)
            print(f"Changed icon of widget '{target_widget.windowTitle()}'")
        else:
            print(f"Widget '{target_widget.windowTitle()}' does not support icons")

