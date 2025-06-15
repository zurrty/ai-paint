from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage, QPen, QColor
from PyQt6.QtCore import Qt, QPoint, QSize # Import QSize for potentially clearer image sizing

class DrawingWidget(QWidget):
    """
    A custom widget that serves as the drawing canvas for the paint application.
    It manages the QImage where drawing operations are performed and handles
    mouse events for interactive drawing.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents) # Optimize for static content (drawing)

        # Initialize QImage with a default size directly here
        # Since resizeEvent is removed, the image will maintain this size unless set_size is called.
        self.image_width = 800
        self.image_height = 600
        self.image = QImage(self.image_width, self.image_height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white) # Fill the image with white background

        self.drawing = False      # Flag to indicate if drawing is in progress
        self.last_point = QPoint() # Stores the last mouse position for continuous drawing

        self.pen_color = Qt.GlobalColor.black # Default pen color
        self.pen_size = 2         # Default pen size

    def set_size(self, w=800, h=600):
        """
        Resizes the internal QImage canvas to the specified width and height.
        Content of the old image is drawn onto the new one to preserve it.
        This method replaces the automatic resizing logic of resizeEvent.
        """
        if w < 1 or h < 1: # Ensure valid dimensions
            print("Warning: Cannot set image size to zero or negative dimensions.")
            return

        # Create a new QImage with the updated size
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        new_image.fill(Qt.GlobalColor.white) # Fill new areas with white

        # Draw the old image onto the new one to preserve existing content
        # This prevents loss of drawing when the canvas size is manually changed.
        painter = QPainter(new_image)
        painter.drawImage(0, 0, self.image) # Draw old image onto new one
        painter.end() # It's good practice to call end() when done with a QPainter on a QImage

        self.image = new_image # Update the image reference
        self.image_width = w   # Update stored dimensions
        self.image_height = h
        self.update()          # Request a repaint of the widget to show the resized image

    def paintEvent(self, event):
        """
        Handles the painting of the widget. This method is called whenever
        the widget needs to be repainted (e.g., when resized or updated).
        It draws the current QImage onto the widget.
        """
        painter = QPainter(self)
        # Ensure the image is drawn scaled to fit the widget's current size
        # if the widget size changes but the image size is constant.
        # Alternatively, if the image size should strictly match the widget,
        # then set_size would need to be called on widget resize via a signal
        # or manual handling in main.py. Given resizeEvent is removed,
        # we draw the fixed-size image, which might lead to cropping/empty space
        # if the widget itself resizes.
        painter.drawImage(0, 0, self.image)

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
            painter.end() # End the painter on the image
            self.last_point = event.pos() # Update the last point
            self.update() # Request a repaint of the widget to show the changes

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release events. Stops drawing.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
