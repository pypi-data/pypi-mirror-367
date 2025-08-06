import tkinter as tk
from tkinter import ttk

def clear_frame(frame):
    """Remove all child widgets from a tkinter frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def create_details_view_placeholder(parent_frame):
    """Creates a placeholder label in the details view."""
    clear_frame(parent_frame)
    placeholder = ttk.Label(parent_frame, text="Select a topic to see details.")
    placeholder.pack(expand=True)
