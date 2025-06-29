from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen # Added QPainter, QPen
from enum import Enum


class BaseTool:
    def __init__(self, size=2, color=Qt.GlobalColor.black): # Default color for tools that use it
        self.size = size
        self.color = color # Specific tools can override or ignore this
        self.tool_type = "base" # Placeholder, can be more specific in subclasses

    _drawing=False
    _canvas_ref = None
    _last_image_pos = QPointF()

    def activate(self, canvas, image_pos):
        self._canvas = canvas
        self._last_image_pos = image_pos
        self._drawing = True
        self._canvas_ref = canvas

    def move(self, image_pos):
        """Handles movement while the tool is active (e.g., drawing a line)."""
        if not self._drawing or not self._canvas_ref:
            return
        # Base implementation does nothing, subclasses override.
        pass

    def deactivate(self):
        self._drawing = False
        # self._canvas_ref = None # Optional: clear reference for strict cleanup

class BrushTool(BaseTool):
    def __init__(self, size=2, color=Qt.GlobalColor.black):
        super().__init__(size, color)

    def activate(self, canvas, image_pos): # Override to draw a dot on click
        super().activate(canvas, image_pos)
        if self._canvas_ref:
            painter = QPainter(self._canvas_ref.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            pen = QPen(self.color, self.size,
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPoint(image_pos.toPointF())
            painter.end()
            self._canvas_ref.update()

    def move(self, image_pos):
        if not self._drawing or not self._canvas_ref:
            return

        painter = QPainter(self._canvas_ref.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        pen = QPen(self.color, self.size,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self._last_image_pos.toPointF(), image_pos.toPointF())
        painter.end()

        self._last_image_pos = image_pos # Update last position
        self._canvas_ref.update()

class EraserTool(BaseTool):
    def __init__(self, size=10): # Eraser has its own default size, color is fixed
        super().__init__(size, Qt.GlobalColor.white) # Eraser color should be white for RGB32 canvas

    def activate(self, canvas, image_pos):
        super().activate(canvas, image_pos)
        if self._canvas_ref:
            painter = QPainter(self._canvas_ref.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            pen = QPen(self.color, self.size, # Use self.color (which is now white)
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPoint(image_pos.toPointF())
            painter.end()
            self._canvas_ref.update()

    def move(self, image_pos):
        if not self._drawing or not self._canvas_ref:
            return

        painter = QPainter(self._canvas_ref.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        pen = QPen(self.color, self.size,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self._last_image_pos.toPointF(), image_pos.toPointF())
        painter.end()

        self._last_image_pos = image_pos # Update last position
        self._canvas_ref.update()


class Tools(Enum):
    """
    Enum for tool types. Values are instances of the tool classes.
    """
    BRUSH = BrushTool()
    ERASER = EraserTool(size=10) # Eraser can have a different default initial size
