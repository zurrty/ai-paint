import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QWidget,
    QInputDialog, QMessageBox, QDialog, QFormLayout
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence # QKeySequence for keyboard shortcuts
from PyQt6.QtCore import Qt

# Import the DrawingWidget from drawing.py
from drawing import Canvas
from dialog import ResizeDialog
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
        self.setWindowTitle("PyQt6 Paint Application")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

        self._create_toolbar() # Call method to create toolbar

        # Optional: Set a window icon
        # self.setWindowIcon(QIcon("path/to/your/icon.png"))

    def _create_toolbar(self):
        """
        Creates and populates the application's toolbar.
        """
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)

        # File Actions
        new_action = QAction("New", self)
        # new_action.setIcon(QIcon("path/to/new_icon.png"))
        self.toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        self.toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        self.toolbar.addAction(save_action)
        save_action.triggered.connect(self.canvas.save_image)


        self.toolbar.addSeparator()

        # Tool Actions
        self.brush_action = QAction("Brush (D)", self)
        # self.brush_action.setIcon(QIcon("path/to/brush_icon.png"))
        self.brush_action.setCheckable(True) # Make it checkable so it stays active
        self.brush_action.setChecked(True) # Brush is default active tool
        self.brush_action.triggered.connect(self._set_brush_tool)
        self.toolbar.addAction(self.brush_action)

        self.eraser_action = QAction("Eraser (E)", self)
        # self.eraser_action.setIcon(QIcon("path/to/eraser_icon.png"))
        self.eraser_action.setCheckable(True)
        self.eraser_action.triggered.connect(self._set_eraser_tool)
        self.toolbar.addAction(self.eraser_action)

        self.toolbar.addSeparator()

        # Image Actions
        resize_action = QAction("Resize Image", self)
        resize_action.triggered.connect(self._show_resize_dialog)
        self.toolbar.addAction(resize_action)

        self.toolbar.addSeparator()

        # Exit Action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.toolbar.addAction(exit_action)

    def _set_brush_tool(self):
        """Sets the active tool to Brush."""
        self.canvas.set_tool(Tools.BRUSH)
        self.brush_action.setChecked(True)
        self.eraser_action.setChecked(False) # Ensure only one tool is active

    def _set_eraser_tool(self):
        """Sets the active tool to Eraser."""
        self.canvas.set_tool(Tools.ERASER)
        self.eraser_action.setChecked(True)
        self.brush_action.setChecked(False) # Ensure only one tool is active

    def _show_resize_dialog(self):
        resize_dialog = ResizeDialog(self.canvas.image_width, self.canvas.image_height, self)
        if resize_dialog.exec() == QDialog.DialogCode.Accepted:
            new_width, new_height = resize_dialog.get_size()
            if new_width is not None and new_height is not None:
                self.canvas.set_size(new_width, new_height)

    def keyPressEvent(self, event):
        """
        Handles keyboard press events for tool selection.
        """
        if event.key() == Qt.Key.Key_D:
            self._set_brush_tool()
        elif event.key() == Qt.Key.Key_E:
            self._set_eraser_tool()
        else:
            super().keyPressEvent(event) # Pass other key events to parent class


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec())