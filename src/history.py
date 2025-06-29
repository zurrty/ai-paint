from collections import deque
from PyQt6.QtGui import QImage


class HistoryManager:
    """
    Manages the undo and redo stacks for the canvas.
    Each state in the history is a QImage object. This class provides the
    core logic for adding states, and performing undo/redo operations.
    """
    def __init__(self, max_history=30):
        """
        Initializes the HistoryManager.
        :param max_history: The maximum number of undo steps to store.
        """
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)

    def clear(self):
        """Clears both the undo and redo stacks. Used for new/loaded images."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def add_state(self, image: QImage):
        """
        Adds a new state to the undo stack. This should be a copy of the
        image *before* a change is made. Adding a new state clears the redo stack.
        """
        self.undo_stack.append(image.copy())
        self.redo_stack.clear()

    def undo(self, current_image: QImage) -> QImage | None:
        """
        Performs an undo operation. The current state of the image is pushed
        to the redo stack, and the last state from the undo stack is returned.
        :param current_image: The current QImage on the canvas (the state to be undone).
        :return: The previous QImage state, or None if no undo is possible.
        """
        if not self.can_undo():
            return None

        self.redo_stack.append(current_image.copy())
        return self.undo_stack.pop()

    def redo(self, current_image: QImage) -> QImage | None:
        """
        Performs a redo operation. The current state of the image is pushed
        to the undo stack, and the last state from the redo stack is returned.
        :param current_image: The current QImage on the canvas (the state before redoing).
        :return: The redone QImage state, or None if no redo is possible.
        """
        if not self.can_redo():
            return None

        self.undo_stack.append(current_image.copy())
        return self.redo_stack.pop()

    def can_undo(self) -> bool:
        """Returns True if there are states on the undo stack."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Returns True if there are states on the redo stack."""
        return len(self.redo_stack) > 0