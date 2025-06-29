import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QWidget,
    QInputDialog, QMessageBox, QDialog, QFormLayout, QFileDialog,
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
        self.setWindowTitle("PyQt6 Paint Application")
        self.setGeometry(100, 100, 800, 600)
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        # menu bar
        
        self._create_menubar() # Create menu bar
        self._create_toolbar() # Call method to create toolbar

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
        save_action.triggered.connect(self.canvas.save_image)
        
        self.file_menu.addSeparator()
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit", self)
        self.file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.close)


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
        canvas = new_image_dialog.get_canvas()
        if canvas is not None:
            self.setCentralWidget(canvas)
            self.canvas = canvas


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