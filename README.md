# GCPaint

A simple paint application built with Python and the PyQt6 framework. This project was developed with the assistance of Google's Gemini AI, which helped in generating code, debugging, and implementing features.

## Features

*   **Basic Drawing Tools:** Brush, Eraser, and Flood Fill.
*   **Color Selection:** Choose any color for your brush and fill tools.
*   **Adjustable Tool Size:** Dynamically change the size of the brush and eraser.
*   **Pan & Zoom:** Easily navigate the canvas using the mouse wheel for zooming and middle-mouse or spacebar + left-mouse for panning.
*   **File Operations:** Create new images, open existing ones, and save your work in various formats (PNG, JPG, BMP).
*   **Undo/Redo:** Robust history management allows for multiple levels of undo and redo.
*   **Image Resizing:** Change the dimensions of your canvas on the fly.

## Setup and Installation

To run this application, you'll need Python 3. Follow these steps to set up the project locally.

### 1. Clone the Repository (Optional)

If you have git installed, you can clone the repository.

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies. The `venv` module is a great choice for this.

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

With the virtual environment activated, install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Usage

To launch the application, run the `main.py` script from the `src` directory:

```bash
python src/main.py
```