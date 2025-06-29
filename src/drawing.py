from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QTransform
from PyQt6.QtCore import Qt, QPoint, QPointF, pyqtSignal
from tools import Tools, BrushTool, EraserTool, FillTool
from history import HistoryManager

class Canvas(QWidget):
    """
    A custom widget that serves as the drawing canvas for the paint application.
    It manages the QImage where drawing operations are performed and handles
    mouse events for interactive drawing, including pan and zoom.
    Supports different drawing tools like brush and eraser.
    """

    historyChanged = pyqtSignal()

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

        # History management
        self.history_manager = HistoryManager()

        # Drawing state
        self.drawing = False

        # Tool properties
        self.tool_size = 2         # Default generic tool size
        self.brush_color = QColor(Qt.GlobalColor.black) # Main color for drawing tools
        self.current_tool = Tools.BRUSH.value # Get the BrushTool instance
        self.current_tool.size = self.tool_size # Apply initial canvas tool size to the tool
        self.current_tool.color = self.brush_color # Apply initial canvas color to the tool

        # Pan and Zoom state
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.panning = False
        self.spacebar_panning_active = False
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
            return
        self.add_history_state()

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

    def new_image(self, w, h, color):
        """Re-initializes the canvas with a new blank image, clearing history."""
        self.image = QImage(w, h, QImage.Format.Format_RGB32)
        self.image.fill(color)
        self.image_width = w
        self.image_height = h
        self.image_path = None

        self.history_manager.clear()
        self.historyChanged.emit()
        self.update()

    def add_history_state(self):
        """Adds the current image state to the undo stack."""
        self.history_manager.add_state(self.image)
        self.historyChanged.emit()

    def undo(self):
        """Performs an undo operation and updates the canvas."""
        undone_image = self.history_manager.undo(self.image)
        if undone_image:
            self.image = undone_image
            self.image_width = self.image.width()
            self.image_height = self.image.height()
            self.historyChanged.emit()
            self.update()

    def redo(self):
        """Performs a redo operation and updates the canvas."""
        redone_image = self.history_manager.redo(self.image)
        if redone_image:
            self.image = redone_image
            self.historyChanged.emit()
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
        # If the new tool uses the main brush color, apply it
        if isinstance(self.current_tool, (BrushTool, FillTool)):
            self.current_tool.color = self.brush_color
        self.update()

    def set_brush_color(self, color):
        """Sets the main brush color and applies it to the current tool if it's a brush or fill tool."""
        self.brush_color = color
        if isinstance(self.current_tool, (BrushTool, FillTool)):
            self.current_tool.color = self.brush_color

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

            self.history_manager.clear()
            self.historyChanged.emit()

            # Reset pan and zoom to fit the new image
            self.zoom_factor = 1.0
            self.pan_offset = QPoint(0, 0)
            self._update_transform()
            self.update()
            return True
        return False

    def save_image(self):
        """
        Saves the current image. If a path is already known, it overwrites the
        file. Otherwise, it calls `save_image_as()` to prompt the user for a path.
        Returns True on success, False on failure.
        """
        if self.image_path:
            return self.image.save(self.image_path)
        else:
            return self.save_image_as()

    def save_image_as(self):
        """
        Prompts the user for a file path and saves the current image to that location.
        Updates the internal image_path on success.
        Returns True on success or user cancellation. Returns False on a save error.
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As...", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return True # User cancelled, which is not an error state.

        self.image_path = file_path
        return self.image.save(self.image_path) # Returns True on success, False on error

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
        # Pan if middle-mouse is clicked, or if spacebar is held and left-mouse is clicked
        if (event.button() == Qt.MouseButton.MiddleButton) or \
           (self.spacebar_panning_active and event.button() == Qt.MouseButton.LeftButton):
            self.panning = True
            self.last_pan_point = event.pos()
            if self.spacebar_panning_active:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.LeftButton:
            # Map the widget coordinates to image coordinates for drawing
            self.add_history_state()
            image_pos = self.transform.inverted()[0].map(event.pos())
            self.current_tool.activate(self, image_pos)
            if self.current_tool._drawing: # Check if tool successfully activated
                 self.drawing = True # Canvas's drawing flag for mouseMove/Release
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
        elif self.panning and (event.buttons() & (Qt.MouseButton.LeftButton | Qt.MouseButton.MiddleButton)):
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
            if self.panning:
                self.panning = False
                if self.spacebar_panning_active:
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
            elif self.drawing:
                self.current_tool.deactivate()
                self.drawing = False # Reset canvas drawing flag
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False

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

    def keyPressEvent(self, event):
        """Handles key presses for activating spacebar panning."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.spacebar_panning_active = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Handles key releases for deactivating spacebar panning."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.spacebar_panning_active = False
            self.panning = False # Ensure panning stops when space is released
            self.unsetCursor()
        else:
            super().keyReleaseEvent(event)
