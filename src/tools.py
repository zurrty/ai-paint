from collections import deque
from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QPainter, QPen
from enum import Enum


class BaseTool:
    def __init__(self, size=2, color=Qt.GlobalColor.black): # Default color for tools that use it
        self.size = size
        self.color = color # Specific tools can override or ignore this

    _drawing=False
    _canvas = None
    _last_image_pos = QPointF()

    def activate(self, canvas, image_pos):
        self._last_image_pos = image_pos
        self._drawing = True
        self._canvas = canvas

    def move(self, image_pos):
        """Handles movement while the tool is active (e.g., drawing a line)."""
        if not self._drawing or not self._canvas:
            return
        # Base implementation does nothing, subclasses override.
        pass

    def deactivate(self):
        self._drawing = False

class BrushTool(BaseTool):
    def __init__(self, size=2, color=Qt.GlobalColor.black):
        super().__init__(size, color)

    def activate(self, canvas, image_pos): # Override to draw a dot on click
        super().activate(canvas, image_pos)
        if self._canvas:
            painter = QPainter(self._canvas.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            pen = QPen(self.color, self.size,
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPoint(image_pos.toPointF())
            painter.end()
            self._canvas.update()

    def move(self, image_pos):
        if not self._drawing or not self._canvas:
            return

        painter = QPainter(self._canvas.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        pen = QPen(self.color, self.size,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self._last_image_pos.toPointF(), image_pos.toPointF())
        painter.end()

        self._last_image_pos = image_pos # Update last position
        self._canvas.update()


class FillTool(BaseTool):
    """
    A tool for filling an area of the same color with a new color.
    Uses a queue-based flood fill algorithm.
    """
    def __init__(self, color=Qt.GlobalColor.black):
        # Fill tool doesn't use size, but needs color
        super().__init__(size=1, color=color)

    def activate(self, canvas, image_pos):
        """
        Activates the fill. This is a single-shot action that performs
        the flood fill and then finishes.
        """
        super().activate(canvas, image_pos)
        image = self._canvas.image
        start_point = image_pos

        if not image.rect().contains(start_point):
            self.deactivate()
            return

        target_rgb = image.pixel(start_point)
        fill_rgb = self.color.rgba()

        if target_rgb == fill_rgb:
            self.deactivate()
            return

        q = deque([start_point])
        visited = {start_point}

        while q:
            p = q.popleft()
            image.setPixel(p, fill_rgb)

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = QPoint(p.x() + dx, p.y() + dy)

                if image.rect().contains(neighbor) and neighbor not in visited and image.pixel(neighbor) == target_rgb:
                    visited.add(neighbor)
                    q.append(neighbor)

        self._canvas.update()
        self.deactivate()

    def move(self, image_pos):
        # Fill tool is a single-click action, so move does nothing.
        pass


class EraserTool(BaseTool):
    def __init__(self, size=10): # Eraser has its own default size, color is fixed
        super().__init__(size, Qt.GlobalColor.white) # Eraser color should be white for RGB32 canvas

    def activate(self, canvas, image_pos):
        super().activate(canvas, image_pos)
        if self._canvas:
            painter = QPainter(self._canvas.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            pen = QPen(self.color, self.size, # Use self.color (which is now white)
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPoint(image_pos.toPointF())
            painter.end()
            self._canvas.update()

    def move(self, image_pos):
        if not self._drawing or not self._canvas:
            return

        painter = QPainter(self._canvas.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        pen = QPen(self.color, self.size,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self._last_image_pos.toPointF(), image_pos.toPointF())
        painter.end()

        self._last_image_pos = image_pos # Update last position
        self._canvas.update()


class Tools(Enum):
    """
    Enum for tool types. Values are instances of the tool classes.
    """
    BRUSH = BrushTool()
    ERASER = EraserTool(size=10) # Eraser can have a different default initial size
    FILL = FillTool()
