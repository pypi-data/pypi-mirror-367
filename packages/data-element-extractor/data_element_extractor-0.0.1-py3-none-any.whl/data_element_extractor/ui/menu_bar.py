import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import uuid
from ..cde_server_service import get_all_cdes, get_cde_lists_from_server, load_data_element_list_from_server, CDEServerService
from ..inference_server_service import InferenceServerService
from ..extractor import MockText
from ..config import config

class MenuBar:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.extractor = app.extractor
        self.choice_symbol_var = tk.StringVar(value=config.get_choice_symbol_config())
        self.constrained_output_var = tk.BooleanVar(value=config.get_constrained_output_config())
        self.cde_server_service = CDEServerService()
        self.inference_server_service = InferenceServerService()

    def create_menu(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        # File menu
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Topic File", command=self.new_topic_file)
        self.file_menu.add_command(label="Open Topics...", command=self.open_topics)
        self.file_menu.add_command(label="Load Topics from Server...", command=self._show_server_topics_popup)
        self.file_menu.add_command(label="Load List from Server...", command=self._show_server_lists_popup)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save Topics", command=self.save_topics)
        self.file_menu.add_command(label="Save Topics As...", command=self.save_as_topics)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Create new Prompt for Selected Topic", command=self.create_new_prompt_for_selected_topic)
        self.file_menu.add_command(label="Create new Prompts for All Topics", command=self.create_new_prompts_for_all_topics)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Create Few-Shot Prompt for Selected Topic", command=self._create_few_shot_prompt_for_selected_topic)
        self.file_menu.add_command(label="Create Few-Shot Prompts for All Topics", command=self._create_few_shot_prompts_for_all_topics)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        # Settings menu
        self.settings_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Configure Server Settings", command=self.open_server_settings)
        
        # --- Choice Symbols Submenu ---
        self.choice_symbols_menu = tk.Menu(self.settings_menu, tearoff=0)
        self.settings_menu.add_cascade(label="Choice Symbols", menu=self.choice_symbols_menu)

        self.choice_symbols_menu.add_radiobutton(
            label="None", variable=self.choice_symbol_var, value="none", 
            command=self._update_choice_symbol_config
        )
        self.choice_symbols_menu.add_radiobutton(
            label="Alphabetical (A, B, C...)", variable=self.choice_symbol_var, value="alphabetical", 
            command=self._update_choice_symbol_config
        )
        self.choice_symbols_menu.add_radiobutton(
            label="Numerical (1, 2, 3...)", variable=self.choice_symbol_var, value="numerical", 
            command=self._update_choice_symbol_config
        )
        self.choice_symbols_menu.add_separator()
        self.choice_symbols_menu.add_command(label="Custom Symbols...", command=self._set_custom_symbols)
        # --- Constrained Output Submenu ---
        self.constrained_output_menu = tk.Menu(self.settings_menu, tearoff=0)
        self.settings_menu.add_cascade(label="Constrained Output", menu=self.constrained_output_menu)
        self.constrained_output_menu.add_radiobutton(
            label="None", variable=self.constrained_output_var, value=False, 
            command=self._update_constrained_output_config
        )
        self.constrained_output_menu.add_radiobutton(
            label="Constrained", variable=self.constrained_output_var, value=True, 
            command=self._update_constrained_output_config
        )
        # Bind keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda event: self.new_topic_file())
        self.root.bind_all("<Control-o>", lambda event: self.open_topics())
        self.root.bind_all("<Control-s>", lambda event: self.save_topics())
        self.root.bind_all("<Control-S>", lambda event: self.save_as_topics()) # Ctrl+Shift+S


    def _update_choice_symbol_config(self):
        selection = self.choice_symbol_var.get()
        config.set_choice_symbol_config(selection)
        self.app.status_var.set(f"Choice symbols set to: {selection}")


    def _update_constrained_output_config(self):
        selection = self.constrained_output_var.get()
        config.set_constrained_output_config(selection)
        self.app.status_var.set(f"Constrained output set to: {selection}")

    def _set_custom_symbols(self):
        custom_symbols_str = simpledialog.askstring(
            "Custom Symbols",
            "Enter custom symbols, separated by commas (e.g., sym1,sym2,sym3)",
            parent=self.root
        )
        if custom_symbols_str:
            # Basic validation: ensure not empty and contains commas for multiple symbols
            if ',' not in custom_symbols_str and len(custom_symbols_str.strip()) > 1:
                 messagebox.showwarning("Custom Symbols", "For a single custom symbol, please ensure it's a single token or character.")

            self.choice_symbol_var.set(custom_symbols_str) # Set the variable to the custom string
            self._update_choice_symbol_config()

    def open_server_settings(self):
        popup = tk.Toplevel(self.root)
        popup.title("Server Settings")
        popup.geometry("400x200")

        cde_server_url_label = tk.Label(popup, text="CDE Server URL:")
        cde_server_url_label.pack()

        cde_server_url_entry = tk.Entry(popup)
        cde_server_url_entry.pack()

        cde_server_url_entry.insert(0, self.cde_server_service.get_cde_server_url())


        inference_server_url_label = tk.Label(popup, text="Inference Server URL:")
        inference_server_url_label.pack()

        inference_server_url_entry = tk.Entry(popup)
        inference_server_url_entry.pack()

        inference_server_url_entry.insert(0, self.inference_server_service.get_inference_server_url())

        def save_settings():
            new_cde_server_url = cde_server_url_entry.get()
            new_inference_server_url = inference_server_url_entry.get()
            if new_cde_server_url:
                self.cde_server_service.set_cde_server_url(new_cde_server_url)
            if new_inference_server_url:
                self.inference_server_service.set_inference_server_url(new_inference_server_url)
            messagebox.showinfo("Settings", "Server URLs updated successfully.")
            popup.destroy()

        save_button = tk.Button(popup, text="Save", command=save_settings)
        save_button.pack()

    def _confirm_unsaved_changes(self):
        # Basic check, can be enhanced to track actual modifications
        if self.extractor.get_topics(): # A simple proxy for 'has content'
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                                 "You have unsaved changes. Save before proceeding?")
            if response is True: # Yes
                self.save_topics()
                return True
            elif response is False: # No
                return True
            else: # Cancel
                return False
        return True # No changes or user chose not to save

    def new_topic_file(self):
        # Potentially ask for confirmation if there are unsaved changes
        self.extractor.remove_all_topics()
        self.app.current_file_path = None
        self.app.status_var.set("New topic file created.")
        #Refresh topics list
        self.app.topics_view._refresh_topics_list()
        messagebox.showinfo("New Extractor", "New extractor instance created.")

    def open_topics(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                # The extractor instance is reset and topics are loaded by the method
                self.extractor.load_topics(filepath)
                self.app.current_file_path = filepath
                self.app.status_var.set(f"Topics loaded from {os.path.basename(filepath)}")
                self.app.topics_view._refresh_topics_list()
                messagebox.showinfo("Open Topics", f"Topics loaded from {filepath}")
            except Exception as e:
                self.app.status_var.set(f"Error loading topics: {e}")
                messagebox.showerror("Error", f"Failed to load topics: {e}")

    def save_topics(self):
        if self.app.current_file_path:
            try:
                self.extractor.save_topics(self.app.current_file_path)
                self.app.status_var.set(f"Topics saved to {os.path.basename(self.app.current_file_path)}")
                messagebox.showinfo("Save Topics", f"Topics saved to {self.app.current_file_path}")
            except Exception as e:
                self.app.status_var.set(f"Error saving topics: {e}")
                messagebox.showerror("Error", f"Failed to save topics: {e}")
        else:
            self.save_as_topics()

    def save_as_topics(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                self.extractor.save_topics(filepath)
                self.app.current_file_path = filepath
                self.app.status_var.set(f"Topics saved as {os.path.basename(filepath)}")
                messagebox.showinfo("Save Topics", f"Topics saved to {filepath}")
            except Exception as e:
                self.app.status_var.set(f"Error saving topics: {e}")
                messagebox.showerror("Error", f"Failed to save topics: {e}")



    def create_new_prompt_for_selected_topic(self):
        selected_items = self.app.topics_view.topics_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a topic from the list first.")
            return
        topic_id = selected_items[0]
        topic = self.extractor.get_topic_by_id(topic_id)
        self.extractor.generate_improved_prompt(
                topic_id=topic_id,
                topic_name=topic['topic_input'].value,
                topic_categories_list=[cat['name'].value for cat in topic.get('categories', [])]
            )
        self.app.topics_view._populate_details_view(topic_id)
        messagebox.showinfo("Success", "New prompt created for selected topic.")
        self.app.status_var.set(f"New prompt created for topic {topic_id}.")

       


    def create_new_prompts_for_all_topics(self):
        self.extractor.create_new_prompts_for_all_topics()
        self.app.topics_view._refresh_topics_list()
        messagebox.showinfo("Success", "New prompts created for all topics.")
        self.app.status_var.set("New prompts created for all topics.")
        


    def _create_few_shot_prompt_for_selected_topic(self):
        selected_items = self.app.topics_view.topics_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a topic from the list first.")
            return
        
        topic_id = selected_items[0]
        dataset_path = filedialog.askopenfilename(
            title="Select CSV for Few-Shot Examples",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not dataset_path:
            return

        params = simpledialog.askstring(
            "Input Parameters", 
            "Enter: text_col,label_col,delimiter,num_examples", 
            initialvalue="0,1,;,3"
        )
        if not params:
            return
            
        try:
            text_col, label_col, delimiter, num_examples = params.split(',')
            text_col, label_col, num_examples = int(text_col), int(label_col), int(num_examples)
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid format. Please use: text_col,label_col,delimiter,num_examples")
            return

        try:
            self.extractor.create_few_shot_prompt(
                topic_id=topic_id,
                csv_path=dataset_path,
                text_col_idx=text_col,
                label_col_idx=label_col,
                delimiter=delimiter,
                num_examples=num_examples
            )
            # Refresh the view to show the new prompt
            self.app.topics_view._populate_details_view(topic_id)
            messagebox.showinfo("Success", "Few-shot prompt created successfully.")
            self.app.status_var.set(f"Few-shot prompt created for topic {topic_id}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create few-shot prompt: {e}")
            self.app.status_var.set(f"Error creating few-shot prompt: {e}")

    def _create_few_shot_prompts_for_all_topics(self):
        if not self.extractor.get_topics():
            messagebox.showinfo("Info", "Please add at least one topic before creating few-shot prompts.")
            return

        filepath = filedialog.askopenfilename(
            title="Select CSV for Few-Shot Prompts",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return

        num_examples = simpledialog.askinteger(
            "Number of Examples",
            "Enter the number of examples for the few-shot prompts:",
            initialvalue=3,
            minvalue=1,
            parent=self.root
        )
        if num_examples is None:
            return

        try:
            self.extractor.create_few_shot_prompts_for_all_topics(filepath, num_examples=num_examples)
            self.app.topics_view._refresh_topics_list()
            self.app.status_var.set("Few-shot prompts created for all topics.")
            messagebox.showinfo("Success", "Few-shot prompts created for all topics.")
        except Exception as e:
            self.app.status_var.set(f"Error creating few-shot prompts: {e}")
            messagebox.showerror("Error", f"Failed to create few-shot prompts: {e}")


    def _show_server_topics_popup(self):
        try:
            server_cdes = get_all_cdes()
            if not server_cdes:
                messagebox.showinfo("Load from Server", "No 'Value List' CDEs found on the server or server is unavailable.")
                return
        except Exception as e:
            messagebox.showerror("Server Error", f"Failed to connect to the server or fetch data: {e}")
            return

        popup = tk.Toplevel(self.app.root)
        popup.title("Load Topics from Server")
        popup.geometry("400x500")

        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.server_topic_vars = {}
        for cde in server_cdes:
            var = tk.BooleanVar()
            cde_id = cde.get('id')
            cde_name = cde.get('name', 'Unnamed CDE')
            self.server_topic_vars[cde_id] = (var, cde)
            cb = ttk.Checkbutton(scrollable_frame, text=f"{cde_name} ({cde_id})", variable=var)
            cb.pack(anchor=tk.W, padx=10, pady=2)

        buttons_frame = ttk.Frame(popup)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        load_button = ttk.Button(buttons_frame, text="Load Selected", command=lambda: self._load_selected_server_topics(popup))
        load_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=popup.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def _load_selected_server_topics(self, popup):
        selected_topics = [(cde_id, cde_data) for cde_id, (var, cde_data) in self.server_topic_vars.items() if var.get()]

        if not selected_topics:
            messagebox.showinfo("No Selection", "No topics were selected to load.", parent=popup)
            return

        # General confirmation before proceeding
        num_selected = len(selected_topics)
        if not messagebox.askyesno("Confirm Load", f"You are about to load {num_selected} topic(s). This may overwrite existing topics with the same ID. Continue?", parent=popup):
            return

        for cde_id, cde_data in selected_topics:
            self.extractor.load_data_element_from_server(cde_id)
        self.app.topics_view._refresh_topics_list()
        popup.destroy()
    def _show_server_lists_popup(self):
        try:
            server_lists = get_cde_lists_from_server()
            if not server_lists:
                messagebox.showinfo("Load from Server", "No CDE Lists found on the server or server is unavailable.")
                return
        except Exception as e:
            messagebox.showerror("Server Error", f"Failed to connect to the server or fetch data: {e}")
            return

        popup = tk.Toplevel(self.app.root)
        popup.title("Load CDE List from Server")
        popup.geometry("450x400")

        # Store lists for later retrieval
        self.server_lists_data = {f"{lst.get('name', 'Unnamed')} ({lst.get('id')})": lst for lst in server_lists}

        listbox_frame = ttk.Frame(popup)
        listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        listbox_label = ttk.Label(listbox_frame, text="Select a CDE List to load:")
        listbox_label.pack(anchor=tk.W)

        self.server_lists_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, exportselection=False)
        for display_text in self.server_lists_data.keys():
            self.server_lists_listbox.insert(tk.END, display_text)
        
        self.server_lists_listbox.pack(fill="both", expand=True, pady=5)

        buttons_frame = ttk.Frame(popup)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        load_button = ttk.Button(buttons_frame, text="Load Selected", command=lambda: self._load_selected_server_list(popup))
        load_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=popup.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)


    def _load_selected_server_list(self, popup):
        selected_indices = self.server_lists_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("No Selection", "No list was selected to load.", parent=popup)
            return
        selected_display_text = self.server_lists_listbox.get(selected_indices[0])
        selected_list_data = self.server_lists_data[selected_display_text]
        list_id = selected_list_data.get('id')
        self.extractor.load_data_element_list_from_server(list_id)
        self.app.topics_view._refresh_topics_list()
        popup.destroy()
