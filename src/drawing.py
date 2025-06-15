from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QTransform # Import QTransform
from PyQt6.QtCore import Qt, QPoint, QPointF # Import QPointF for float precision

class DrawingWidget(QWidget):
    """
    A custom widget that serves as the drawing canvas for the paint application.
    It manages the QImage where drawing operations are performed and handles
    mouse events for interactive drawing, including pan and zoom.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents) # Optimize for static content (drawing)

        # Image properties
        self.image_width = 800
        self.image_height = 600
        self.image = QImage(self.image_width, self.image_height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white) # Fill the image with white background

        # Drawing state
        self.drawing = False      # Flag to indicate if drawing is in progress
        self.last_drawing_point_image = QPointF() # Stores the last mouse position in image coordinates for drawing

        self.pen_color = Qt.GlobalColor.black # Default pen color
        self.pen_size = 2         # Default pen size

        # Pan and Zoom state
        self.zoom_factor = 1.0    # Current zoom level (1.0 = actual size)
        self.pan_offset = QPoint(0, 0) # Current pan offset in widget coordinates
        self.panning = False      # Flag to indicate if panning is in progress
        self.last_pan_point = QPoint() # Stores the last mouse position for panning

        # Transformation matrix for drawing and viewing
        self.transform = QTransform()
        self._update_transform() # Initialize the transform

        # Set focus policy to enable receiving keyboard events (e.g., for future shortcuts)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _update_transform(self):
        """
        Updates the internal QTransform based on current pan offset and zoom factor.
        This transform is used by the painter and for coordinate mapping.
        """
        self.transform.reset()
        self.transform.translate(self.pan_offset.x(), self.pan_offset.y())
        self.transform.scale(self.zoom_factor, self.zoom_factor)

    def set_size(self, w, h):
        """
        Resizes the internal QImage canvas to the specified width and height.
        Content of the old image is drawn onto the new one to preserve it.
        This method replaces the automatic resizing logic of resizeEvent.
        When the image is resized, reset pan/zoom for a clear view of the new canvas.
        """
        if w < 1 or h < 1: # Ensure valid dimensions
            print("Warning: Cannot set image size to zero or negative dimensions.")
            return

        # Create a new QImage with the updated size
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        new_image.fill(Qt.GlobalColor.white) # Fill new areas with white

        # Draw the old image onto the new one to preserve existing content
        painter = QPainter(new_image)
        painter.drawImage(0, 0, self.image) # Draw old image onto new one
        painter.end() # It's good practice to call end() when done with a QPainter on a QImage

        self.image = new_image # Update the image reference
        self.image_width = w   # Update stored dimensions
        self.image_height = h

        # Reset pan and zoom when the image canvas size changes
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self._update_transform() # Update the transform with new reset values
        self.update()          # Request a repaint of the widget to show the resized image


    def paintEvent(self, event):
        """
        Handles the painting of the widget. This method is called whenever
        the widget needs to be repainted (e.g., when resized or updated).
        It draws the current QImage onto the widget using the current
        pan and zoom transformation.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True) # Optional: for smoother lines/graphics
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True) # For smoother scaled image

        # Apply the transformation for pan and zoom
        painter.setTransform(self.transform)

        # Draw the QImage. It will be drawn scaled and translated by the transform.
        painter.drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        """
        Handles mouse press events. Differentiates between drawing (left click)
        and panning (middle click).
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            # Map the widget coordinates to image coordinates for drawing
            self.last_drawing_point_image = self.transform.inverted()[0].map(event.pos())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.last_pan_point = event.pos() # Store the initial point for panning
        self.update()

    def mouseMoveEvent(self, event):
        """
        Handles mouse move events. Continues drawing or panning based on active flags.
        """
        if self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            # Get current point in image coordinates
            current_drawing_point_image = self.transform.inverted()[0].map(event.pos())

            painter = QPainter(self.image) # Create a QPainter to draw on the QImage
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(QPen(self.pen_color, self.pen_size,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                Qt.PenJoinStyle.RoundJoin))
            # Draw line on the QImage using image coordinates
            painter.drawLine(self.last_drawing_point_image.toPointF(), current_drawing_point_image.toPointF())
            painter.end() # End the painter on the image

            self.last_drawing_point_image = current_drawing_point_image # Update the last point for next segment
            self.update() # Request a repaint of the widget to show the changes

        elif self.panning and event.buttons() & Qt.MouseButton.MiddleButton:
            delta = event.pos() - self.last_pan_point # Calculate movement vector
            self.pan_offset += delta # Apply delta to pan offset
            self.last_pan_point = event.pos() # Update last point for next move

            self._update_transform() # Update the transformation matrix
            self.update() # Request a repaint

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release events. Stops drawing or panning.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
        self.update()

    def wheelEvent(self, event):
        """
        Handles mouse wheel events for zooming in and out.
        Zooms towards the mouse cursor's position.
        """
        old_zoom_factor = self.zoom_factor
        zoom_in_factor = 1.15
        zoom_out_factor = 0.85

        # Determine zoom direction based on scroll direction
        # event.angleDelta().y() gives 120 for one click up, -120 for one click down
        if event.angleDelta().y() > 0: # Scroll up (zoom in)
            self.zoom_factor *= zoom_in_factor
        else: # Scroll down (zoom out)
            self.zoom_factor *= zoom_out_factor

        # Clamp zoom factor to a reasonable range
        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0)) # Example: Min 0.1x, Max 10x

        # Adjust pan offset to keep the point under the mouse cursor fixed (zoom to mouse)
        # Corrected: Use event.position() for QWheelEvent
        view_pos = event.position().toPoint() # Mouse position in widget coordinates

        # Calculate the point in image coordinates BEFORE the zoom
        image_pos_before_zoom = self.transform.inverted()[0].map(view_pos)

        # Recalculate pan offset based on the new zoom factor
        # The screen point (view_pos) should still correspond to image_pos_before_zoom
        # after the new transformation: view_pos = new_pan_offset + image_pos_before_zoom * new_zoom_factor
        # So: new_pan_offset = view_pos - image_pos_before_zoom * new_zoom_factor
        self.pan_offset = view_pos - image_pos_before_zoom * self.zoom_factor

        self._update_transform() # Update the transformation matrix
        self.update() # Request a repaint
