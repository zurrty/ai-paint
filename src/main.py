import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QWidget
from PyQt6.QtGui import QIcon, QAction # QAction will be used for toolbar buttons
from PyQt6.QtCore import Qt

# Import the DrawingWidget from the new drawing.py file
from drawing import DrawingWidget

# Pillow (PIL) import - included for future use, not directly used in this basic window
from PIL import Image

class PaintApp(QMainWindow):
    """
    The main application window for the PyQt6 Paint application.
    Initializes the main window and sets up the DrawingWidget as its central widget.
    Also adds a horizontal toolbar at the top.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Paint Application") # Set the window title
        self.setGeometry(100, 100, 800, 600)          # Set window position (x, y) and size (width, height)

        # Create an instance of our custom DrawingWidget
        self.drawing_widget = DrawingWidget(self)
        self.setCentralWidget(self.drawing_widget) # Set it as the central widget

        # --- Add a horizontal toolbar ---
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False) # Make the toolbar fixed

        # Example: Add some actions to the toolbar (these don't do anything yet)
        # You'll add actual functionalities later
        new_action = QAction("New", self)
        # new_action.setIcon(QIcon("path/to/new_icon.png")) # Uncomment to add an icon
        self.toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        self.toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        self.toolbar.addAction(save_action)

        # Add a separator for better organization
        self.toolbar.addSeparator()

        # Another example action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close) # Connect exit action to close the window
        self.toolbar.addAction(exit_action)
        # --- End of toolbar setup ---

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
