import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QWidget,
    QInputDialog, QMessageBox # QInputDialog for getting user input
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

# Import the DrawingWidget from the new drawing.py file
from drawing import DrawingWidget

# Pillow (PIL) import - included for future use, not directly used in this basic window
from PIL import Image

class PaintApp(QMainWindow):
    """
    The main application window for the PyQt6 Paint application.
    Initializes the main window and sets up the DrawingWidget as its central widget.
    Also adds a horizontal toolbar at the top with a new resize action.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Paint Application")
        self.setGeometry(100, 100, 800, 600)

        # Create an instance of our custom DrawingWidget
        self.drawing_widget = DrawingWidget(self)
        self.setCentralWidget(self.drawing_widget)

        # --- Add a horizontal toolbar ---
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)

        # Example: Add some actions to the toolbar (these don't do anything yet)
        new_action = QAction("New", self)
        self.toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        self.toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        self.toolbar.addAction(save_action)

        self.toolbar.addSeparator()

        # --- New: Resize Image Action ---
        resize_action = QAction("Resize Image", self)
        resize_action.triggered.connect(self._show_resize_dialog) # Connect to the new method
        self.toolbar.addAction(resize_action)
        # --- End New Action ---

        self.toolbar.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.toolbar.addAction(exit_action)
        # --- End of toolbar setup ---

        # Optional: Set a window icon
        # self.setWindowIcon(QIcon("path/to/your/icon.png"))

    def _show_resize_dialog(self):
        """
        Opens a dialog to get new width and height from the user for resizing the image.
        """
        current_width = self.drawing_widget.image_width
        current_height = self.drawing_widget.image_height

        # Get new width from user
        new_width, ok_width = QInputDialog.getInt(
            self,
            "Resize Image",
            f"Enter new width (current: {current_width}px):",
            current_width, # Default value
            1,             # Minimum value
            4000,          # Maximum value
            1              # Step
        )

        if ok_width: # If user clicked OK for width
            # Get new height from user
            new_height, ok_height = QInputDialog.getInt(
                self,
                "Resize Image",
                f"Enter new height (current: {current_height}px):",
                current_height, # Default value
                1,              # Minimum value
                4000,           # Maximum value
                1               # Step
            )

            if ok_height: # If user clicked OK for height
                # Call the set_size method of the drawing widget
                self.drawing_widget.set_size(new_width, new_height)
                QMessageBox.information(
                    self,
                    "Image Resized",
                    f"Image resized to {new_width}x{new_height} pixels."
                )
            else:
                QMessageBox.information(self, "Resize Canceled", "Image height input canceled.")
        else:
            QMessageBox.information(self, "Resize Canceled", "Image width input canceled.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec())
