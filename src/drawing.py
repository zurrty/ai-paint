from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QTransform
from PyQt6.QtCore import Qt, QPoint, QPointF

# Define tool constants for clarity
class Tools:
    BRUSH = 0
    ERASER = 1

class DrawingWidget(QWidget):
    """
    A custom widget that serves as the drawing canvas for the paint application.
    It manages the QImage where drawing operations are performed and handles
    mouse events for interactive drawing, including pan and zoom.
    Supports different drawing tools like brush and eraser.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)

        # Image properties
        self.image_width = 800
        self.image_height = 600
        self.image = QImage(self.image_width, self.image_height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white) # Fill the image with white background

        # Drawing state
        self.drawing = False
        self.last_drawing_point_image = QPointF()

        # Tool properties
        self.current_tool = Tools.BRUSH # Default tool is brush
        self.brush_color = Qt.GlobalColor.black # Default brush color
        self.brush_size = 2         # Default brush size

        self.eraser_size = 10       # Default eraser size (larger)

        # Pan and Zoom state
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.panning = False
        self.last_pan_point = QPoint()

        # Transformation matrix for drawing and viewing
        self.transform = QTransform()
        self._update_transform()

        # Set focus policy to enable receiving keyboard events
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
        When the image is resized, reset pan/zoom for a clear view of the new canvas.
        """
        if w < 1 or h < 1:
            print("Warning: Cannot set image size to zero or negative dimensions.")
            return

        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        new_image.fill(Qt.GlobalColor.white)

        painter = QPainter(new_image)
        painter.drawImage(0, 0, self.image)
        painter.end()

        self.image = new_image
        self.image_width = w
        self.image_height = h

        # Reset pan and zoom when the image canvas size changes
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self._update_transform()
        self.update()

    def set_tool(self, tool):
        """Sets the active drawing tool."""
        self.current_tool = tool
        self.update() # Update to reflect potential cursor change (not implemented yet, but good practice)

    def set_brush_color(self, color):
        """Sets the brush color."""
        self.brush_color = color

    def set_brush_size(self, size):
        """Sets the brush size."""
        self.brush_size = size

    def set_eraser_size(self, size):
        """Sets the eraser size."""
        self.eraser_size = size

    def paintEvent(self, event):
        """
        Handles the painting of the widget. It draws the current QImage onto the widget
        using the current pan and zoom transformation.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        painter.setTransform(self.transform)
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
            self.last_pan_point = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        """
        Handles mouse move events. Continues drawing or panning based on active flags.
        Applies current tool properties (color, size).
        """
        if self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            current_drawing_point_image = self.transform.inverted()[0].map(event.pos())

            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            # Set pen based on the current tool
            if self.current_tool == Tools.BRUSH:
                painter.setPen(QPen(self.brush_color, self.brush_size,
                                    Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                    Qt.PenJoinStyle.RoundJoin))
            elif self.current_tool == Tools.ERASER:
                painter.setPen(QPen(Qt.GlobalColor.white, self.eraser_size, # Eraser draws with white color
                                    Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                    Qt.PenJoinStyle.RoundJoin))

            painter.drawLine(self.last_drawing_point_image.toPointF(), current_drawing_point_image.toPointF())
            painter.end()

            self.last_drawing_point_image = current_drawing_point_image
            self.update()

        elif self.panning and event.buttons() & Qt.MouseButton.MiddleButton:
            delta = event.pos() - self.last_pan_point
            self.pan_offset += delta
            self.last_pan_point = event.pos()

            self._update_transform()
            self.update()

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
        zoom_in_factor = 1.15
        zoom_out_factor = 0.85

        if event.angleDelta().y() > 0: # Scroll up (zoom in)
            self.zoom_factor *= zoom_in_factor
        else: # Scroll down (zoom out)
            self.zoom_factor *= zoom_out_factor

        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))

        view_pos = event.position().toPoint()
        image_pos_before_zoom = self.transform.inverted()[0].map(view_pos)

        self.pan_offset = view_pos - image_pos_before_zoom * self.zoom_factor

        self._update_transform()
        self.update()

