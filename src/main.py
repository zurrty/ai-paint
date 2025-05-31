import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, QPoint

class PaintApp(QMainWindow):
    """
    The main application window for the PyQt6 Paint application.
    Initializes an empty window with a title and a default size.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Paint Application") # Set the window title
        self.setGeometry(100, 100, 800, 600)          # Set window position (x, y) and size (width, height)

        # Create a central widget for the main window.
        # All other UI elements will be placed inside this central widget.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Optional: Set a background color for the central widget to make it visible
        self.central_widget.setStyleSheet("background-color: #F0F0F0;") # Light gray background

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