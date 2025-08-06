import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from .ui_helpers import clear_frame, create_details_view_placeholder
import threading
from ..cde_server_service import get_all_cdes
from ..extractor import MockText
from .think_config_view import ThinkConfigView

class TopicsView:
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.extractor = app.extractor
        self.improve_button = None

        # PanedWindow for Topics and Details
        self.main_paned_window = ttk.PanedWindow(parent_frame, orient=tk.HORIZONTAL)
        parent_frame.add(self.main_paned_window, weight=1)

        # --- Left Panel: Topics List ---
        topics_frame = ttk.Labelframe(self.main_paned_window, text="Topics", padding=5)
        self.main_paned_window.add(topics_frame, weight=1)

        # --- Buttons for Topic Actions ---
        topic_buttons_frame = ttk.Frame(topics_frame)
        topic_buttons_frame.pack(fill=tk.X, pady=(0, 5))

        add_topic_button = ttk.Button(topic_buttons_frame, text="Add Topic", command=self._add_topic)
        add_topic_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        remove_topic_button = ttk.Button(topic_buttons_frame, text="Remove Topic", command=self._remove_selected_topic)
        remove_topic_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))

        up_button = ttk.Button(topic_buttons_frame, text="Up", command=self._move_topic_up)
        up_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))

        down_button = ttk.Button(topic_buttons_frame, text="Down", command=self._move_topic_down)
        down_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))

        self.topics_tree = ttk.Treeview(topics_frame, columns=("id", "name", "type"), show="headings")
        self.topics_tree.heading("id", text="ID")
        self.topics_tree.column("id", width=250, stretch=tk.NO)
        self.topics_tree.heading("name", text="Topic Name")
        self.topics_tree.heading("type", text="Type")
        self.topics_tree.column("type", width=100, stretch=tk.NO)
        self.topics_tree.pack(expand=True, fill=tk.BOTH)
        self.topics_tree.bind("<<TreeviewSelect>>", self._on_topic_select)
        self.topics_tree.bind("<Button-3>", self._show_topics_context_menu) # Right-click

        self._create_topics_context_menu()

        # --- Column 2: Topic Details ---
        self.details_frame = ttk.Labelframe(self.main_paned_window, text="Topic Details", padding=5)
        self.main_paned_window.add(self.details_frame, weight=2)
        create_details_view_placeholder(self.details_frame)

        # --- Column 3: Categories ---
        self.categories_frame = ttk.Labelframe(self.main_paned_window, text="Categories", padding=5)
        # main_paned_window.add(self.categories_frame, weight=1)
        create_details_view_placeholder(self.categories_frame)
        



    def _refresh_topics_list(self):
        # Clear existing items
        for item in self.topics_tree.get_children():
            self.topics_tree.delete(item)
        # Add current topics
        for topic in self.extractor.get_topics():
            topic_type = "Value List" if isinstance(topic.get('topic_data'), list) else topic.get('topic_data', 'Not Set')
            self.topics_tree.insert("", tk.END, iid=topic['id'], values=(topic['id'], topic['topic_input'].value, topic_type))
        create_details_view_placeholder(self.details_frame)
        create_details_view_placeholder(self.categories_frame)




    def _on_topic_select(self, event):
        selected_items = self.topics_tree.selection()
        if selected_items:
            topic_id = selected_items[0]
            topic = self.extractor.get_topic_by_id(topic_id)

            self._populate_details_view(topic_id)

            # Decide whether to show the categories view
            if topic and isinstance(topic.get('topic_data'), list):
                # This is a "Value List" topic, so show and populate categories
                # The panes() method returns widget path names, so we compare strings
                if str(self.categories_frame) not in self.main_paned_window.panes():
                    self.main_paned_window.add(self.categories_frame, weight=1)
                self._populate_categories_view(topic_id)
            else:
                # Not a "Value List" topic, so hide the categories frame
                if str(self.categories_frame) in self.main_paned_window.panes():
                    self.main_paned_window.forget(self.categories_frame)



    def _populate_details_view(self, topic_id):
        clear_frame(self.details_frame)
        topic = self.extractor.get_topic_by_id(topic_id)
        if not topic:
            create_details_view_placeholder(self.details_frame)
            return

        # Topic Name
        ttk.Label(self.details_frame, text=f"Name: {topic['topic_input'].value}").pack(anchor=tk.W)
        ttk.Label(self.details_frame, text=f"ID: {topic['id']}").pack(anchor=tk.W)

        # Data Element Type
        topic_data = topic.get('topic_data')
        if isinstance(topic_data, list):
            data_element_type = "Value List"
        elif isinstance(topic_data, str):
            data_element_type = topic_data.capitalize()
        else:
            data_element_type = "Not Set"
        ttk.Label(self.details_frame, text=f"Data Element Type: {data_element_type}").pack(anchor=tk.W)
        
        # Topic Condition
        condition_frame = ttk.Frame(self.details_frame)
        condition_frame.pack(fill=tk.X, pady=(5,0))

        ttk.Label(condition_frame, text="Condition:").pack(side=tk.LEFT, anchor=tk.W)
        
        self.current_topic_condition_var = tk.StringVar(value=topic['condition'].value)
        condition_entry = ttk.Entry(condition_frame, textvariable=self.current_topic_condition_var, width=40)
        condition_entry.pack(side=tk.LEFT, padx=(5,5), expand=True, fill=tk.X)
        
        set_condition_button = ttk.Button(condition_frame, text="Set Condition", 
                                          command=lambda t_id=topic_id: self._set_topic_condition(t_id))
        set_condition_button.pack(side=tk.LEFT)

        ttk.Separator(self.details_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Prompt Editor
        prompt_frame = ttk.Frame(self.details_frame)
        prompt_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Label(prompt_frame, text="Prompt:").pack(anchor=tk.NW)

        self.prompt_text_area = tk.Text(prompt_frame, height=5, wrap=tk.WORD)
        self.prompt_text_area.pack(expand=True, fill=tk.BOTH, pady=(0, 5))
        
        prompt_object = topic.get('prompt')
        current_prompt_text = ''
        if isinstance(prompt_object, str):
            current_prompt_text = prompt_object
        elif hasattr(prompt_object, 'value'): # Check for .value attribute (like MockText)
            current_prompt_text = prompt_object.value
        
        if current_prompt_text is None: # Ensure it's a string for the Text widget
            current_prompt_text = ''
            
        self.prompt_text_area.delete("1.0", tk.END) # Clear existing content
        self.prompt_text_area.insert(tk.END, current_prompt_text) # Insert new content

        # Action buttons frame for prompt
        prompt_actions_frame = ttk.Frame(prompt_frame)
        prompt_actions_frame.pack(fill=tk.X, pady=(5,0))

        # Iterations for improvement
        ttk.Label(prompt_actions_frame, text="Iterations:").pack(side=tk.LEFT, padx=(0, 5))
        self.iterations_var = tk.StringVar(value='3')
        iterations_entry = ttk.Entry(prompt_actions_frame, textvariable=self.iterations_var, width=5)
        iterations_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Improve Prompt Button
        self.improve_button = ttk.Button(prompt_actions_frame, text="Improve Prompt",
                                    command=lambda t_id=topic_id: self._improve_prompt(t_id))
        self.improve_button.pack(side=tk.LEFT, padx=(0, 5))
        self.update_improve_button_state()

        # Save Prompt Button
        save_prompt_button = ttk.Button(prompt_actions_frame, text="Save Prompt",
                                        command=lambda t_id=topic_id: self._save_topic_prompt(t_id))
        save_prompt_button.pack(side=tk.LEFT)

        ttk.Separator(self.details_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # --- Action Buttons ---
        buttons_frame = ttk.Frame(self.details_frame)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        remove_topic_button = ttk.Button(buttons_frame, text="Remove Topic", command=lambda: self._remove_topic(topic_id))
        remove_topic_button.pack(side=tk.RIGHT)


    def _create_topics_context_menu(self):
        self.topics_context_menu = tk.Menu(self.topics_tree, tearoff=0)
        self.topics_context_menu.add_command(label="Configure Thinking...", command=self._open_think_config_for_topic)
        self.topics_context_menu.add_command(label="Copy Topic ID", command=self._copy_topic_id)

    def _show_topics_context_menu(self, event):
        # Identify row under cursor
        iid = self.topics_tree.identify_row(event.y)
        if not iid:
            return # Do not show menu if not on an item

        # Select the item under the cursor if it's not already selected
        if iid not in self.topics_tree.selection():
            self.topics_tree.selection_set(iid)
            self._on_topic_select(event) # Update details view

        # The menu should only be active if there is exactly one item selected
        if len(self.topics_tree.selection()) == 1:
            self.topics_context_menu.entryconfig("Configure Thinking...", state="normal")
            self.topics_context_menu.entryconfig("Copy Topic ID", state="normal")
        else:
            self.topics_context_menu.entryconfig("Configure Thinking...", state="disabled")
            self.topics_context_menu.entryconfig("Copy Topic ID", state="disabled")

        self.topics_context_menu.post(event.x_root, event.y_root)

    def _open_think_config_for_topic(self):
        selected_items = self.topics_tree.selection()
        if not selected_items:
            return
        
        topic_id = selected_items[0]
        config_view = ThinkConfigView(self.parent_frame, self.app, topic_id=topic_id)
        self.parent_frame.wait_window(config_view)

    def _copy_topic_id(self):
        selected_items = self.topics_tree.selection()
        if not selected_items:
            return
        
        topic_id = selected_items[0]
        self.parent_frame.clipboard_clear()
        self.parent_frame.clipboard_append(topic_id)


    def _create_categories_context_menu(self):
        self.categories_context_menu = tk.Menu(self.categories_tree, tearoff=0)
        self.categories_context_menu.add_command(label="Copy Category ID", command=self._copy_category_id)


    def _show_categories_context_menu(self, event):
        # Identify row under cursor
        iid = self.categories_tree.identify_row(event.y)
        if not iid:
            return # Do not show menu if not on an item

        # Select the item under the cursor if it's not already selected
        if iid not in self.categories_tree.selection():
            self.categories_tree.selection_set(iid)
            # self._on_category_select(event) # Update details view

        # The menu should only be active if there is exactly one item selected
        if len(self.categories_tree.selection()) == 1:
            self.categories_context_menu.entryconfig("Copy Category ID", state="normal")
        else:
            self.categories_context_menu.entryconfig("Copy Category ID", state="disabled")

        self.categories_context_menu.post(event.x_root, event.y_root)

    def _copy_category_id(self):
        selected_items = self.categories_tree.selection()
        if not selected_items:
            return
        # Get the category ID from the selected item, which has an entry with Name and Id in the row
        category_id = self.categories_tree.item(selected_items[0])['values'][1]
        self.parent_frame.clipboard_clear()
        self.parent_frame.clipboard_append(category_id)



    def _populate_categories_view(self, topic_id):
        clear_frame(self.categories_frame)
        topic = self.extractor.get_topic_by_id(topic_id)
        if not topic:
            create_details_view_placeholder(self.categories_frame)
            return

        category_buttons_frame = ttk.Frame(self.categories_frame)
        category_buttons_frame.pack(fill=tk.X, pady=(0, 5))

        add_category_button = ttk.Button(category_buttons_frame, text="Add Category", command=lambda: self._add_category(topic_id))
        add_category_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        remove_category_button = ttk.Button(category_buttons_frame, text="Remove Category", command=lambda: self._remove_category(topic_id))
        remove_category_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))

        self.categories_tree = ttk.Treeview(self.categories_frame, columns=("name", "id"), show="headings")
        self.categories_tree.heading("name", text="Category Name")
        self.categories_tree.column("name", stretch=tk.YES)
        self.categories_tree.heading("id", text="ID")
        self.categories_tree.column("id", width=250, stretch=tk.NO)
        self.categories_tree.bind("<Button-3>", self._show_categories_context_menu) # Right-click

        self._create_categories_context_menu()

        placeholder_label = ttk.Label(self.categories_frame, text="No categories defined.")
        
        topic_categories = topic.get('categories', [])

        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)

        if not topic_categories:
            self.categories_tree.pack_forget()
            placeholder_label.pack(pady=10, anchor=tk.CENTER)
        else:
            placeholder_label.pack_forget()
            self.categories_tree.pack(expand=True, fill=tk.BOTH)
            
            for category_data in topic_categories:
                if isinstance(category_data, tuple) and len(category_data) >= 2 and hasattr(category_data[0], 'value'):
                    self.categories_tree.insert("", tk.END, values=(category_data[0].value, category_data[1]))
                else:
                    print(f"[DEBUG] Skipping malformed category data: {category_data}")



    def _set_topic_condition(self, topic_id):
        topic = self.extractor.get_topic_by_id(topic_id)
        if not topic:
            messagebox.showerror("Error", f"Topic with ID {topic_id} not found.")
            return

        new_condition = self.current_topic_condition_var.get().strip()
        topic['condition'].value = new_condition 
        
        self.app.status_var.set(f"Condition for topic {topic_id} updated to: '{new_condition}'.")



    def _add_topic(self):
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Add New Topic")
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        dialog.geometry("300x150")

        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Topic Name
        ttk.Label(main_frame, text="Topic Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        main_frame.grid_columnconfigure(1, weight=1)

        # Topic Type
        ttk.Label(main_frame, text="Topic Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        topic_type_var = tk.StringVar()
        options = ["Value List", "Text", "Date", "Number"]
        topic_type_var.set(options[1])  # Default to "Text"
        type_menu = ttk.OptionMenu(main_frame, topic_type_var, options[1], *options)
        type_menu.grid(row=1, column=1, sticky=tk.EW, pady=5)

        def on_ok():
            topic_name = name_entry.get().strip()
            topic_type = topic_type_var.get()
            if not topic_name:
                messagebox.showerror("Error", "Topic name cannot be empty.", parent=dialog)
                return

            try:
                # Topic Data is the type of the topic in lowercase, unless it is "Value List", in which case it is an empty list (for the categories)
                topic_data = topic_type.lower() if topic_type != "Value List" else []
                tmpPrompt = "INSTRUCTION: You are a helpful extractor. You select the correct of the possible categories for classifying a piece of text. The topic of the classification is '[TOPIC]'. The allowed categories are '[CATEGORIES]'. QUESTION: The text to be classified is '[TEXT]'. ANSWER: The correct category for this text is '"

                if topic_type=="Number":
                    tmpPrompt = "INSTRUCTION: You are a helpful extractor. You select the correct number value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct number value for this text is '"
                elif topic_type=="Date":
                    tmpPrompt = "INSTRUCTION: You are a helpful extractor. You select the correct date value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct date value for this text is '"
                elif topic_type=="Text":
                    tmpPrompt = "INSTRUCTION: You are a helpful extractor. You select the correct text value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct text value for this text is '"
                
                self.extractor.add_topic(topic_name=topic_name, topic_data=topic_data, prompt=tmpPrompt)
                self._refresh_topics_list()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add topic: {e}", parent=dialog)

        def on_cancel():
            dialog.destroy()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)

        name_entry.focus_set()
        dialog.wait_window()


    def _add_category(self, topic_id):
        category_name = simpledialog.askstring("Add Category", "Enter the new category's name:", parent=self.app.root)
        if category_name and category_name.strip():
            self.extractor.add_category(topic_id, category_name.strip())
            self._populate_categories_view(topic_id) # Refresh categories view


    def _remove_category(self, topic_id):
        selected_items = self.categories_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a category to remove.")
            return

        category_id = self.categories_tree.item(selected_items[0])['values'][1]
        category_name = self.categories_tree.item(selected_items[0])['values'][0]

        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the category '{category_name}'?", parent=self.app.root):
            self.extractor.remove_category(topic_id, category_id)
            self._populate_categories_view(topic_id) # Refresh the view

    def _move_topic_up(self):
        selected_items = self.topics_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a topic to move.")
            return
        topic_id = selected_items[0]
        self.extractor.increase_topic_order(topic_id)
        self._refresh_topics_list()
        self.topics_tree.selection_set(topic_id)

    def _move_topic_down(self):
        selected_items = self.topics_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a topic to move.")
            return
        topic_id = selected_items[0]
        self.extractor.decrease_topic_order(topic_id)
        self._refresh_topics_list()
        self.topics_tree.selection_set(topic_id)

    def _remove_selected_topic(self):
        selected_items = self.topics_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a topic to remove.")
            return
        topic_id = selected_items[0]
        self._remove_topic(topic_id)

    def _remove_topic(self, topic_id):
        topic = self.extractor.get_topic_by_id(topic_id)
        if not topic:
            return # Should not happen if UI is consistent
        
        topic_name = topic['topic_input'].value
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the topic '{topic_name}'?\nThis will also update any conditions that reference this topic.", parent=self.parent_frame):
            self.extractor.remove_topic(topic_id)
            self._refresh_topics_list()


    def _improve_prompt(self, topic_id):
        try:
            iterations = int(self.iterations_var.get())
            if iterations <= 0:
                messagebox.showerror("Error", "Number of iterations must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of iterations.")
            return

        dataset_path = filedialog.askopenfilename(
            title="Select CSV Dataset for Improvement",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not dataset_path:
            return

        params = simpledialog.askstring("Input Parameters", "Enter: text_col_idx,truth_col_idx,delimiter", initialvalue="0,1,;")
        if not params:
            return
        try:
            text_col, truth_col, delimiter = params.split(',')
            text_col, truth_col = int(text_col), int(truth_col)
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid format. Please use: text_col_idx,truth_col_idx,delimiter")
            return

        self.app.status_var.set(f"Starting prompt improvement for topic {topic_id}...")
        thread = threading.Thread(
            target=self._run_improvement_in_thread,
            args=(topic_id, dataset_path, text_col, truth_col, iterations, delimiter)
        )
        thread.start()

    def _run_improvement_in_thread(self, topic_id, dataset_path, text_col, truth_col, iterations, delimiter):
        try:
            self.extractor.iteratively_improve_prompt(
                topic_id=topic_id,
                dataset_path=dataset_path,
                text_column_index=text_col,
                ground_truth_column_index=truth_col,
                num_iterations=iterations,
                delimiter=delimiter,
            )
            self.app.root.after(0, self._update_ui_after_improvement, topic_id, True)
        except Exception as e:
            self.app.root.after(0, self._update_ui_after_improvement, topic_id, False, str(e))

    def _update_ui_after_improvement(self, topic_id, success, error_message=None):
        if success:
            self.app.status_var.set("Prompt improvement finished successfully.")
            messagebox.showinfo("Success", "Prompt has been updated with the improved version.")
            self._populate_details_view(topic_id) # Refresh to show new prompt
        else:
            self.app.status_var.set(f"Error during prompt improvement: {error_message}")
            messagebox.showerror("Improvement Failed", f"An error occurred: {error_message}")




    
    def _save_topic_prompt(self, topic_id):
        topic = self.extractor.get_topic_by_id(topic_id)
        if not topic:
            messagebox.showerror("Error", f"Topic with ID {topic_id} not found.")
            return

        new_prompt_text = self.prompt_text_area.get("1.0", tk.END).strip()
        self.extractor.set_prompt(topic_id, new_prompt_text) # Use extractor's method to handle MockText
        
        self.app.status_var.set(f"Prompt for topic {topic_id} updated.")
        messagebox.showinfo("Success", f"Prompt for topic '{topic['topic_input'].value}' (ID: {topic_id}) updated.")



    def update_improve_button_state(self):
        if self.improve_button and self.improve_button.winfo_exists():
            main_model_exists = bool(self.extractor.model_manager.model_name)
            prompt_model_exists = bool(self.extractor.model_manager.prompt_model_name)
            state = tk.NORMAL if main_model_exists and prompt_model_exists else tk.DISABLED
            self.improve_button.config(state=state)
