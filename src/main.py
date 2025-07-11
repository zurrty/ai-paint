import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QWidget,
    QInputDialog, QMessageBox, QDialog, QFormLayout, QFileDialog, QColorDialog,
    QSlider, QLabel # Added QSlider and QLabel
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence # QKeySequence for keyboard shortcuts
from PyQt6.QtCore import Qt

# Import the DrawingWidget from drawing.py
from drawing import Canvas
from dialog import ResizeDialog, NewImageDialog
from tools import Tools # Import Tools from the new file

# Pillow (PIL) import - included for future use
from PIL import Image

class PaintApp(QMainWindow):
    """
    The main application window for the PyQt6 Paint application.
    Initializes the main window, sets up the DrawingWidget,
    and adds a horizontal toolbar with various actions including
    tool selection and image resizing.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GCPaint")
        self.setGeometry(100, 100, 800, 600)
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        # menu bar
        
        self._create_menubar() # Create menu bar and actions
        self._create_toolbar() # Call method to create toolbar

        self.canvas.historyChanged.connect(self._update_history_actions)
        self._update_history_actions() # Set initial state

        # Optional: Set a window icon
        # self.setWindowIcon(QIcon("path/to/your/icon.png"))
    def _create_menubar(self):
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        # File Actions
        new_action = QAction(QIcon.fromTheme("document-new"), "New", self)
        new_action.triggered.connect(self._new_image_dialog)
        self.file_menu.addAction(new_action)

        open_action = QAction(QIcon.fromTheme("document-open"), "Open", self)
        open_action.triggered.connect(self._open_file_dialog)
        self.file_menu.addAction(open_action)

        save_action = QAction(QIcon.fromTheme("document-save"), "Save", self)
        self.file_menu.addAction(save_action)
        save_action.triggered.connect(self._save_dialog)
        
        save_as_action = QAction(QIcon.fromTheme("document-save-as"), "Save As...", self)
        save_as_action.triggered.connect(self._save_as_dialog)
        self.file_menu.addAction(save_as_action)

        self.file_menu.addSeparator()
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit", self)
        self.file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.close)


        # Edit Menu
        edit_menu = self.menu_bar.addMenu("Edit")
        self.undo_action = QAction(QIcon.fromTheme("edit-undo"), "Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.canvas.undo)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction(QIcon.fromTheme("edit-redo"), "Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.canvas.redo)
        edit_menu.addAction(self.redo_action)

        # Image Actions
        self.image_menu = self.menu_bar.addMenu("Image")
        resize_action = QAction(QIcon.fromTheme("transform-scale"), "Resize Image", self)
        resize_action.triggered.connect(self._show_resize_dialog)
        self.image_menu.addAction(resize_action)


    def _create_toolbar(self):
        """
        Creates and populates the application's toolbar.
        """
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(True)

        # Add history actions
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)
        self.toolbar.addSeparator()


        # Tool Actions
        self.brush_action = QAction(QIcon.fromTheme('draw-brush'), "Brush", self)
        self.brush_action.setShortcut(QKeySequence("D"))
        self.brush_action.setCheckable(True) # Make it checkable so it stays active
        self.brush_action.setChecked(True) # Brush is default active tool
        self.brush_action.triggered.connect(self._set_brush_tool)
        self.toolbar.addAction(self.brush_action)

        self.eraser_action = QAction(QIcon.fromTheme('draw-eraser'), "Eraser", self)
        self.eraser_action.setCheckable(True)
        self.eraser_action.triggered.connect(self._set_eraser_tool)
        self.toolbar.addAction(self.eraser_action)

        # Fill Tool Action
        self.fill_action = QAction(QIcon.fromTheme('format-fill-color'), "Fill", self)
        self.fill_action.setShortcut(QKeySequence("F"))
        self.fill_action.setCheckable(True)
        self.fill_action.triggered.connect(self._set_fill_tool)
        self.toolbar.addAction(self.fill_action)

        # Color Picker Action
        self.color_action = QAction(QIcon.fromTheme('preferences-color'), "Color", self)
        self.color_action.setToolTip("Select Brush Color")
        self.color_action.triggered.connect(self._show_color_dialog)
        self.toolbar.addAction(self.color_action)

        self.toolbar.addSeparator()

        # Brush Size Slider
        self.toolbar.addWidget(QLabel("Brush Size:"))
        self.brush_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.brush_size_slider.setMinimum(1)
        self.brush_size_slider.setMaximum(50) # Max brush size
        self.brush_size_slider.setValue(self.canvas.tool_size) # Initial value from canvas
        self.brush_size_slider.setFixedWidth(150) # Give it a reasonable width
        self.brush_size_slider.valueChanged.connect(self._update_brush_size_from_slider)
        self.toolbar.addWidget(self.brush_size_slider)

        # Label to display current brush size (optional, but good UX)
        self.brush_size_label = QLabel(str(self.canvas.tool_size))
        self.brush_size_label.setFixedWidth(30) # Fixed width for the label
        self.toolbar.addWidget(self.brush_size_label)


        self.toolbar.addSeparator()
    
    def _update_brush_size_from_slider(self, value):
        self.canvas.set_tool_size(value)
        self.brush_size_label.setText(str(value)) # Update label

    def _update_history_actions(self):
        """Enables or disables undo/redo actions based on history availability."""
        self.undo_action.setEnabled(self.canvas.history_manager.can_undo())
        self.redo_action.setEnabled(self.canvas.history_manager.can_redo())

    def _show_color_dialog(self):
        """Opens a color dialog to select a new brush color."""
        initial_color = self.canvas.brush_color
        color = QColorDialog.getColor(initial_color, self, "Select Brush Color")

        if color.isValid():
            self.canvas.set_brush_color(color)

    def _set_brush_tool(self):
        """Sets the active tool to Brush."""
        self.canvas.set_tool(Tools.BRUSH)
        self.brush_action.setChecked(True)
        self.eraser_action.setChecked(False)
        self.fill_action.setChecked(False)

    def _set_eraser_tool(self):
        """Sets the active tool to Eraser."""
        self.canvas.set_tool(Tools.ERASER)
        self.eraser_action.setChecked(True)
        self.brush_action.setChecked(False)
        self.fill_action.setChecked(False)

    def _set_fill_tool(self):
        """Sets the active tool to Fill."""
        self.canvas.set_tool(Tools.FILL)
        self.fill_action.setChecked(True)
        self.brush_action.setChecked(False)
        self.eraser_action.setChecked(False)

    def _save_dialog(self):
        """Handles the save action, showing an error if it fails."""
        if not self.canvas.save_image():
            QMessageBox.warning(
                self, "Save Error", "Could not save the image to the specified path."
            )

    def _save_as_dialog(self):
        """Handles the 'Save As' action, showing an error if it fails."""
        if not self.canvas.save_image_as():
            QMessageBox.warning(
                self, "Save Error", "Could not save the image to the specified path."
            )

    def _show_resize_dialog(self):
        resize_dialog = ResizeDialog(self.canvas.image_width, self.canvas.image_height, self)
        if resize_dialog.exec() == QDialog.DialogCode.Accepted:
            new_width, new_height = resize_dialog.get_size()
            if new_width is not None and new_height is not None:
                self.canvas.set_size(new_width, new_height)

    def _open_file_dialog(self):
        """Opens a file dialog to select an image and loads it into the canvas."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            if not self.canvas.load_image(file_path):
                QMessageBox.warning(
                    self, "Open Error", f"Could not open the image file:\n{file_path}"
                )

    def _new_image_dialog(self):
        new_image_dialog = NewImageDialog(self)
        if new_image_dialog.exec() == QDialog.DialogCode.Accepted:
            width, height, color = new_image_dialog.get_values()
            if width and height and color.isValid():
                self.canvas.new_image(width, height, color)

    def keyPressEvent(self, event):
        """
        Handles keyboard press events for tool selection.
        """
        if event.key() == Qt.Key.Key_D:
            self._set_brush_tool()
        elif event.key() == Qt.Key.Key_E:
            self._set_eraser_tool()
        elif event.key() == Qt.Key.Key_F:
            self._set_fill_tool()
        else:
            super().keyPressEvent(event) # Pass other key events to parent class


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec())