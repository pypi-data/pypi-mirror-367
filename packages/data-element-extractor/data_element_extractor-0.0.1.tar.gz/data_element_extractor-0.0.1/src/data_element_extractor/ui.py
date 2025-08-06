import tkinter as tk
from .ui.menu_bar import MenuBar

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Data Element Extractor UI")
        self.label.pack(pady=20, padx=50)

def main():
    root = tk.Tk()
    root.title("Data Element Extractor")
    menu_bar = MenuBar(root)
    root.config(menu=menu_bar)
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()

from .ui.main_app import ExtractorApp

def launch_ui():
    root = tk.Tk()
    app = ExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    launch_ui()
