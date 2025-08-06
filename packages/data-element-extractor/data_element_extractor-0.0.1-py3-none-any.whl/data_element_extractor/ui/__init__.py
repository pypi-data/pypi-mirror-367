import tkinter as tk
from .main_app import ExtractorApp

def launch_ui():
    """Launches the Data Element Extractor UI."""
    root = tk.Tk()
    app = ExtractorApp(root)
    root.mainloop()


