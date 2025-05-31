import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Import the DrawingWidget from the new drawing.py file
from drawing import DrawingWidget

# Pillow (PIL) import - included for future use, not directly used in this basic window
from PIL import Image

class PaintApp(QMainWindow):
    """
    The main application window for the PyQt6 Paint application.
    Initializes the main window and sets up the DrawingWidget as its central widget.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Paint Application") # Set the window title
        self.setGeometry(100, 100, 800, 600)          # Set window position (x, y) and size (width, height)

        # Create an instance of our custom DrawingWidget
        self.drawing_widget = DrawingWidget(self)
        self.setCentralWidget(self.drawing_widget) # Set it as the central widget

        # Optional: Set a window icon (uncomment and provide a path if you have an icon file)
        # self.setWindowIcon(QIcon("path/to/your/icon.png"))

if __name__ == "__main__":
    # Create the QApplication instance. This is necessary for any PyQt6 application.
    app = QApplication(sys.argv)

    # Create an instance of our PaintApp window.
    window = PaintApp()

    # Show the window.
    window.show()

    # Start the application's event loop. This keeps the application running
    # until the user closes the window.
    sys.exit(app.exec())