import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QWidget,
    QInputDialog, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence # QKeySequence for keyboard shortcuts
from PyQt6.QtCore import Qt

# Import the DrawingWidget from drawing.py
from drawing import Canvas
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

        self.drawing_widget = Canvas(self)
        self.setCentralWidget(self.drawing_widget)

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
        self.drawing_widget.set_tool(Tools.BRUSH)
        self.brush_action.setChecked(True)
        self.eraser_action.setChecked(False) # Ensure only one tool is active

    def _set_eraser_tool(self):
        """Sets the active tool to Eraser."""
        self.drawing_widget.set_tool(Tools.ERASER)
        self.eraser_action.setChecked(True)
        self.brush_action.setChecked(False) # Ensure only one tool is active

    def _show_resize_dialog(self):
        """
        Opens a dialog to get new width and height from the user for resizing the image.
        """
        current_width = self.drawing_widget.image_width
        current_height = self.drawing_widget.image_height

        new_width, ok_width = QInputDialog.getInt(
            self, "Resize Image", f"Enter new width (current: {current_width}px):",
            current_width, 1, 4000, 1
        )

        if ok_width:
            new_height, ok_height = QInputDialog.getInt(
                self, "Resize Image", f"Enter new height (current: {current_height}px):",
                current_height, 1, 4000, 1
            )
            if ok_height:
                self.drawing_widget.set_size(new_width, new_height)
                QMessageBox.information(
                    self, "Image Resized", f"Image resized to {new_width}x{new_height} pixels."
                )
            else:
                QMessageBox.information(self, "Resize Canceled", "Image height input canceled.")
        else:
            QMessageBox.information(self, "Resize Canceled", "Image width input canceled.")

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
