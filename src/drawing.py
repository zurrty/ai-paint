from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage, QPen, QColor
from PyQt6.QtCore import Qt, QPoint

class DrawingWidget(QWidget):
    """
    A custom widget that serves as the drawing canvas for the paint application.
    It manages the QImage where drawing operations are performed and handles
    mouse events for interactive drawing.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents) # Optimize for static content (drawing)

        # Initialize QImage with a default size (will be resized by resizeEvent)
        # It's good practice to start with a reasonable size, or let resizeEvent handle initial setup.
        self.image = QImage(800, 600, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white) # Fill the image with white background

        self.drawing = False      # Flag to indicate if drawing is in progress
        self.last_point = QPoint() # Stores the last mouse position for continuous drawing

        self.pen_color = Qt.GlobalColor.black # Default pen color
        self.pen_size = 2         # Default pen size

    def set_size(w=800,h=600):
        # Create a new QImage with the updated widget size  
        new_image = QImage((w,h), QImage.Format.Format_RGB32)
        new_image.fill(Qt.GlobalColor.white) # Fill new areas with white

        # Draw the old image onto the new one to preserve content
        painter = QPainter(new_image)
        painter.drawImage(0, 0, self.image)
        self.image = new_image # Update the image reference

        super().resizeEvent(event)
    def paintEvent(self, event):
        """
        Handles the painting of the widget. This method is called whenever
        the widget needs to be repainted (e.g., when resized or updated).
        It draws the current QImage onto the widget.
        """
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image) # Draw the QImage at (0,0) of the widget

    def mousePressEvent(self, event):
        """
        Handles mouse press events. Starts drawing if the left mouse button
        is pressed.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.pos() # Store the initial point

    def mouseMoveEvent(self, event):
        """
        Handles mouse move events. If drawing is in progress, it draws a line
        from the last point to the current point on the QImage.
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image) # Create a QPainter to draw on the QImage
            painter.setPen(QPen(self.pen_color, self.pen_size,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.last_point, event.pos()) # Draw a line on the QImage
            self.last_point = event.pos() # Update the last point
            self.update() # Request a repaint of the widget to show the changes

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release events. Stops drawing.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
        