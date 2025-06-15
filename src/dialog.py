from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QColorDialog, QSpinBox
from PyQt6.QtGui import QColor

from drawing import Canvas

class NewImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Image")
        self.width_input = QSpinBox()
        self.width_input.setMinimum(1)
        self.width_input.setMaximum(0xffff)
        self.width_input.setValue(800)


        self.height_input = QSpinBox()
        self.height_input.setMinimum(1)
        self.height_input.setMaximum(0xffff)
        self.height_input.setValue(600)

        self.background_color_input = QColorDialog(QColor(0, 0, 0))

        layout = QFormLayout(self)
        layout.addRow("Width:", self.width_input)
        layout.addRow("Height:", self.height_input)
        layout.addRow("Background Color:", self.background_color_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addRow(button_box)
    
    def get_canvas(self):
        if self.exec() == QDialog.DialogCode.Accepted:
            try:
                width = int(self.width_input.value())
                height = int(self.height_input.value())
                background_color = self.background_color_input.selectedColor()
                canvas = Canvas()
                canvas.set_size(width, height)
                canvas.image.fill(background_color)
                return canvas
            except ValueError:
                return None
        else:
            return None 
        


class ResizeDialog(QDialog):
    """
    A custom dialog for getting new width and height values from the user
    to resize the image canvas.
    """
    def __init__(self, current_width, current_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize Image")

        layout = QFormLayout(self)

        self.width_input = QLineEdit(str(current_width))
        self.height_input = QLineEdit(str(current_height))

        layout.addRow("New Width:", self.width_input)
        layout.addRow("New Height:", self.height_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addRow(button_box)

    def get_size(self):
        """
        Returns the entered width and height as integers.
        Returns None, None if input is invalid.
        """
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            if width > 0 and height > 0:
                return width, height
            else:
                return None, None
        except ValueError:
            return None, None

        width_input = QLineEdit(str(current_width))
        height_input = QLineEdit(str(current_height))

        layout.addRow("New Width:", width_input)
        layout.addRow("New Height:", height_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(resize_dialog.accept)
        button_box.rejected.connect(resize_dialog.reject)

        layout.addRow(button_box)

        if resize_dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                new_width = int(width_input.text())
                new_height = int(height_input.text())
                if new_width > 0 and new_height > 0:
                    return new_width, new_height
                else:
                    return None, None
            except ValueError:
                return None, None
        else:
            return None, None