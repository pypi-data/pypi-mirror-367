import tkinter as tk
from tkinter import ttk, messagebox

class ThinkConfigView(tk.Toplevel):
    def __init__(self, parent, app, topic_id=None):
        super().__init__(parent)
        self.app = app
        self.extractor = app.extractor
        self.topic_id = topic_id

        if self.topic_id:
            topic = self.extractor.get_topic_by_id(self.topic_id)
            # This is a dictionary
            self.config_source = topic
            self.title(f"Thinking for Topic: {topic['topic_input'].value}")
            config_dict = topic.get('thinking_config', {})
        else:
            # This is the extractor object
            self.config_source = self.extractor
            self.title("Configure Global Default Thinking")
            config_dict = self.extractor.thinking_config

        self.geometry("600x400")

        # Load existing or default configuration
        self.initial_config = config_dict.get('think_steps', [])
        self.think_steps_data = []

        self._create_widgets()
        self._populate_steps()

    def _create_widgets(self):
        self.steps_frame = ttk.Frame(self)
        self.steps_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.add_step_button = ttk.Button(self, text="Add Step", command=self._add_step_row)
        self.add_step_button.pack(pady=5)

        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        self.save_button = ttk.Button(buttons_frame, text="Save", command=self._save_config)
        self.save_button.pack(side="left", expand=True)

        self.cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side="right", expand=True)

    def _populate_steps(self):
        for step_data in self.initial_config:
            self._add_step_row(step_data)

    def _add_step_row(self, step_data=None):
        row_index = len(self.think_steps_data)
        step_frame = ttk.Frame(self.steps_frame)
        step_frame.pack(fill="x", pady=2)

        ttk.Label(step_frame, text=f"Step {row_index + 1}:").grid(row=0, column=0, padx=5)

        ttk.Label(step_frame, text="Max New Tokens:").grid(row=0, column=1)
        max_tokens_var = tk.StringVar(value=str(step_data.get('max_new_tokens', '50')) if step_data else '50')
        max_tokens_entry = ttk.Entry(step_frame, textvariable=max_tokens_var, width=5)
        max_tokens_entry.grid(row=0, column=2)

        ttk.Label(step_frame, text="Stop Tokens (csv):").grid(row=0, column=3)
        stop_tokens_var = tk.StringVar(value=",".join(step_data.get('stop_tokens', [])) if step_data else '.')
        stop_tokens_entry = ttk.Entry(step_frame, textvariable=stop_tokens_var, width=15)
        stop_tokens_entry.grid(row=0, column=4)

        ttk.Label(step_frame, text="Add Text:").grid(row=0, column=5)
        add_text_var = tk.StringVar(value=step_data.get('add_text', '') if step_data else ' ')
        add_text_entry = ttk.Entry(step_frame, textvariable=add_text_var, width=15)
        add_text_entry.grid(row=0, column=6)

        remove_button = ttk.Button(step_frame, text="X", command=lambda f=step_frame: self._remove_step_row(f), width=2)
        remove_button.grid(row=0, column=7, padx=5)

        step_widgets = {
            'frame': step_frame,
            'max_tokens': max_tokens_var,
            'stop_tokens': stop_tokens_var,
            'add_text': add_text_var
        }
        self.think_steps_data.append(step_widgets)

    def _remove_step_row(self, frame_to_remove):
        index_to_remove = -1
        for i, step in enumerate(self.think_steps_data):
            if step['frame'] == frame_to_remove:
                index_to_remove = i
                break

        if index_to_remove != -1:
            self.think_steps_data.pop(index_to_remove)
            frame_to_remove.destroy()
            for i, step in enumerate(self.think_steps_data):
                step['frame'].winfo_children()[0].config(text=f"Step {i + 1}:")

    def _save_config(self):
        new_config = {'think_steps': []}
        for step_widgets in self.think_steps_data:
            try:
                max_tokens = int(step_widgets['max_tokens'].get())
                stop_tokens = [token.strip() for token in step_widgets['stop_tokens'].get().split(',') if token.strip()]
                add_text = step_widgets['add_text'].get()

                new_config['think_steps'].append({
                    'max_new_tokens': max_tokens,
                    'stop_tokens': stop_tokens,
                    'add_text': add_text
                })
            except ValueError:
                messagebox.showerror("Invalid Input", "'Max New Tokens' must be an integer.", parent=self)
                return

        # Save the updated configuration to the correct source (topic or global)
        if self.topic_id:
            topic = self.extractor.get_topic_by_id(self.topic_id)
            if topic:
                topic['thinking_config'] = new_config
                self.app.status_var.set(f"Thinking config for topic '{topic['topic_input'].value}' updated.")
                messagebox.showinfo("Success", "Topic-specific thinking configuration has been saved.", parent=self)
        else:
            self.extractor.thinking_config = new_config
            self.app.status_var.set("Global thinking configuration updated.")
            messagebox.showinfo("Success", "Global default thinking configuration has been saved.", parent=self)
        
        self.destroy()
