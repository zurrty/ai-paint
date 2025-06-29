from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QTransform
from PyQt6.QtCore import Qt, QPoint, QPointF
from tools import Tools, BrushTool, EraserTool # Be more specific or use from tools import *


class Canvas(QWidget):
    """
    A custom widget that serves as the drawing canvas for the paint application.
    It manages the QImage where drawing operations are performed and handles
    mouse events for interactive drawing, including pan and zoom.
    Supports different drawing tools like brush and eraser.
    """

    # Path to image file
    image_path = None
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
        # self.last_drawing_point_image = QPointF() # Moved to tool instance

        # Tool properties
        self.tool_size = 2         # Default generic tool size
        self.current_tool = Tools.BRUSH.value # Get the BrushTool instance
        self.current_tool.size = self.tool_size # Apply initial canvas tool size
        # self.brush_color attribute removed, color is managed by the tool instance or set via set_current_tool_color

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
        """Sets the active drawing tool from the Tools enum."""
        if self.drawing: # If a tool is currently active, deactivate it first
            self.current_tool.deactivate()
            self.drawing = False

        self.current_tool = tool.value # tool is an enum member like Tools.BRUSH
        # Apply the canvas's current generic tool size to the newly selected tool
        if hasattr(self.current_tool, 'size'):
            self.current_tool.size = self.tool_size
        self.update()

    def set_current_tool_color(self, color):
        """Sets the color for the current tool, if applicable (e.g., Brush)."""
        # EraserTool manages its own color (white) and should not be changed by this.
        if hasattr(self.current_tool, 'color') and not isinstance(self.current_tool, EraserTool):
            self.current_tool.color = color

    def set_tool_size(self, size):
        """Sets the generic tool size and applies it to the current tool."""
        self.tool_size = max(1, size) # Ensure size is at least 1
        if hasattr(self.current_tool, 'size'):
            self.current_tool.size = self.tool_size

    def load_image(self, file_path):
        """
        Loads an image from a specified file path.
        If successful, the canvas is updated with the new image,
        and the view is reset.
        Returns True on success, False on failure.
        """
        new_image = QImage()
        if new_image.load(file_path):
            # Convert to a format that we can reliably draw on.
            self.image = new_image.convertToFormat(QImage.Format.Format_RGB32)
            self.image_width = self.image.width()
            self.image_height = self.image.height()
            self.image_path = file_path  # Store path for future saves

            # Reset pan and zoom to fit the new image
            self.zoom_factor = 1.0
            self.pan_offset = QPoint(0, 0)
            self._update_transform()
            self.update()
            return True
        return False

    def save_image(self):
        """Saves the current image to a file."""
        if type(self.image_path) == str:
            self.image.save(self.image_path)
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            if file_path:
                self.image_path = file_path
                self.save_image()


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
            # Map the widget coordinates to image coordinates for drawing
            image_pos = self.transform.inverted()[0].map(event.pos())
            self.current_tool.activate(self, image_pos)
            if self.current_tool._drawing: # Check if tool successfully activated
                 self.drawing = True # Canvas's drawing flag for mouseMove/Release
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.last_pan_point = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        """
        Handles mouse move events. Continues drawing or panning based on active flags.
        Applies current tool properties (color, size).
        """
        if self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            current_drawing_point_image = self.transform.inverted()[0].map(event.pos())
            self.current_tool.move(current_drawing_point_image)
            # self.update() # Tool's move method should call update

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
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.current_tool.deactivate()
            self.drawing = False # Reset canvas drawing flag
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
        # self.update() # Usually not needed on release unless visual state changes

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
