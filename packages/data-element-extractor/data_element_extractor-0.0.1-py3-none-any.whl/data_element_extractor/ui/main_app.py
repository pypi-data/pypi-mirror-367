import tkinter as tk
from tkinter import ttk

from ..extractor import DataElementExtractor
from .model_config_view import ModelConfigView
from .extractor_view import ExtractorView
from .topics_view import TopicsView
from .menu_bar import MenuBar


class ExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Element Extractor UI")

        self.extractor = DataElementExtractor()
        self.current_file_path = None

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        self.create_widgets()
        self.topics_view._refresh_topics_list() # Initial population

    def create_widgets(self):
        # Menu
        self.menu_bar = MenuBar(self.root, self)
        self.menu_bar.create_menu()

        # Main layout with a PanedWindow
        main_paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned_window.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # --- Top Panel: Model Configuration ---
        model_config_frame = ttk.Labelframe(main_paned_window, text="Model Configuration", padding=5)
        main_paned_window.add(model_config_frame, weight=0)
        self.model_config_view = ModelConfigView(model_config_frame, self)

        # --- Middle Panel: Topics and Details ---
        self.topics_view = TopicsView(main_paned_window, self)



        # --- Bottom Panel: Extraction Tasks ---
        extractor_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(extractor_frame, weight=1)
        self.extractor_view = ExtractorView(extractor_frame, self)

        # --- Status Bar ---
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)





