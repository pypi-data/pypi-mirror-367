import tkinter as tk
from tkinter import ttk, messagebox

class ModelConfigView:
    def __init__(self, parent_frame, app):
        self.app = app
        self.extractor = app.extractor
        self.model_config_frame = parent_frame
        self.config_mode = 'main'

        self.model_type_var = tk.StringVar()
        self.model_name_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.inference_type_var = tk.StringVar()
        self.attn_implementation_var = tk.StringVar(value="flash_attention_2")
        self.move_to_gpu_var = tk.BooleanVar(value=True)

        self._create_model_config_widgets()
        self._refresh_ui_for_mode()
        self._update_model_status_display()

    def _create_model_config_widgets(self):
        # Switch Mode Button
        self.switch_button = ttk.Button(self.model_config_frame, command=self._toggle_config_mode)
        self.switch_button.grid(row=0, column=2, padx=5, pady=2, sticky=tk.E)

        # Model Type
        ttk.Label(self.model_config_frame, text="Model Type:").grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)
        self.model_type_combo = ttk.Combobox(self.model_config_frame, textvariable=self.model_type_var,
                                             values=["Transformers", "OpenAI"], state="readonly")
        self.model_type_combo.grid(row=0, column=1, padx=2, pady=2, sticky=tk.EW)
        self.model_type_combo.bind("<<ComboboxSelected>>", self._on_model_type_change)

        # Model Name
        ttk.Label(self.model_config_frame, text="Model Name/Path:").grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)
        self.model_name_entry = ttk.Entry(self.model_config_frame, textvariable=self.model_name_var)
        self.model_name_entry.grid(row=1, column=1, padx=2, pady=2, sticky=tk.EW)

        # API Key
        self.api_key_label = ttk.Label(self.model_config_frame, text="API Key:")
        self.api_key_label.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)
        self.api_key_entry = ttk.Entry(self.model_config_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.grid(row=2, column=1, padx=2, pady=2, sticky=tk.EW)

        # Inference Type
        ttk.Label(self.model_config_frame, text="Inference Type:").grid(row=3, column=0, padx=2, pady=2, sticky=tk.W)
        self.inference_type_combo = ttk.Combobox(self.model_config_frame, textvariable=self.inference_type_var, state="readonly")
        self.inference_type_combo.grid(row=3, column=1, padx=2, pady=2, sticky=tk.EW)

        # Attn Implementation
        self.attn_label = ttk.Label(self.model_config_frame, text="Attn Implementation:")
        self.attn_label.grid(row=4, column=0, padx=2, pady=2, sticky=tk.W)
        self.attn_entry = ttk.Entry(self.model_config_frame, textvariable=self.attn_implementation_var)
        self.attn_entry.grid(row=4, column=1, padx=2, pady=2, sticky=tk.EW)

        # Move to GPU
        self.gpu_check = ttk.Checkbutton(self.model_config_frame, text="Move to GPU", variable=self.move_to_gpu_var, onvalue=True, offvalue=False)
        self.gpu_check.grid(row=5, column=0, columnspan=2, padx=2, pady=2, sticky=tk.W)


        # Set Model Button
        self.set_model_button = ttk.Button(self.model_config_frame, command=self._set_model)
        self.set_model_button.grid(row=6, column=0, columnspan=3, pady=5)

        # Set Model as Prompt Model Button
        self.set_model_as_prompt_model_button = ttk.Button(self.model_config_frame, text="Set Model as Prompt Model", command=self._set_model_as_prompt_model)
        self.set_model_as_prompt_model_button.grid(row=7, column=0, columnspan=3, pady=5)

        # Status display
        status_frame = ttk.Frame(self.model_config_frame)
        status_frame.grid(row=8, column=0, columnspan=3, pady=(5,0), sticky=tk.EW)
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)

        self.main_model_status_label = ttk.Label(status_frame, text="", font=('Helvetica', 9))
        self.main_model_status_label.grid(row=0, column=0, sticky=tk.W)

        self.prompt_model_status_label = ttk.Label(status_frame, text="", font=('Helvetica', 9))
        self.prompt_model_status_label.grid(row=0, column=1, sticky=tk.E)
        status_frame.columnconfigure(1, weight=1)

        self.main_model_status_label = ttk.Label(status_frame, text="", font=('Helvetica', 9))
        self.main_model_status_label.grid(row=0, column=0, sticky=tk.W)

        self.prompt_model_status_label = ttk.Label(status_frame, text="", font=('Helvetica', 9))
        self.prompt_model_status_label.grid(row=0, column=1, sticky=tk.E)

        self.model_config_frame.columnconfigure(1, weight=1)


    def _toggle_config_mode(self):
        self.config_mode = 'prompt' if self.config_mode == 'main' else 'main'
        self._refresh_ui_for_mode()

    def _refresh_ui_for_mode(self):
        if self.config_mode == 'main':
            # Correctly get data from ModelManager attributes
            model_data = {
                'type': self.extractor.model_manager.model_type,
                'name': self.extractor.model_manager.model_name,
                'inference_type': self.extractor.model_manager.inference_type,
                'attn_implementation': self.extractor.model_manager.attn_implementation,
                'move_to_gpu': self.extractor.model_manager.move_to_gpu
            }
            self.model_config_frame.config(text="Main Model Configuration")
            self.switch_button.config(text="Configure Prompt Model")
            self.set_model_button.config(text="Set Main Model")
            default_type, default_inference = "Transformers", "transformers"
        else:  # 'prompt'
            # Correctly get data from ModelManager attributes for prompt model
            model_data = {
                'type': self.extractor.model_manager.prompt_model_type,
                'name': self.extractor.model_manager.prompt_model_name,
                'inference_type': self.extractor.model_manager.prompt_inference_type,
                'attn_implementation': self.extractor.model_manager.prompt_attn_implementation,
                'move_to_gpu': self.extractor.model_manager.prompt_move_to_gpu
            }
            self.model_config_frame.config(text="Prompt Model Configuration")
            self.switch_button.config(text="Configure Main Model")
            self.set_model_button.config(text="Set Prompt Model")
            default_type, default_inference = "OpenAI", "cloud"

        # Populate UI fields from the collected data
        self.model_type_var.set(model_data.get('type') or default_type)
        self.model_name_var.set(model_data.get('name', ''))
        self.api_key_var.set('') # API key is not stored, so clear the field
        self.inference_type_var.set(model_data.get('inference_type') or default_inference)
        self.attn_implementation_var.set(model_data.get('attn_implementation') or "flash_attention_2")
        self.move_to_gpu_var.set(model_data.get('move_to_gpu', True))
        self._on_model_type_change()
        self._update_model_status_display()

    def _on_model_type_change(self, event=None):
        model_type = self.model_type_var.get()
        if model_type == "OpenAI":
            self.api_key_entry.config(state=tk.NORMAL)
            self.api_key_label.config(state=tk.NORMAL)
            self.inference_type_combo.config(values=["cloud"])
            self.inference_type_var.set("cloud")
            self.attn_label.config(state=tk.DISABLED)
            self.attn_entry.config(state=tk.DISABLED)
            self.gpu_check.config(state=tk.DISABLED)
        elif model_type == "Transformers":
            self.api_key_entry.config(state=tk.DISABLED)
            self.api_key_label.config(state=tk.DISABLED)
            self.api_key_var.set("")
            self.inference_type_combo.config(values=["transformers", "cloud", "server"])
            if self.inference_type_var.get() not in ["transformers", "cloud", "server"]:
                self.inference_type_var.set("transformers")
            self.attn_label.config(state=tk.NORMAL)
            self.attn_entry.config(state=tk.NORMAL)
            self.gpu_check.config(state=tk.NORMAL)

    def _update_model_status_display(self):
        # Main model status
        main_model_name = self.extractor.model_manager.model_name
        if main_model_name:
            self.main_model_status_label.config(text=f"Main: {main_model_name}", foreground="green")
        else:
            self.main_model_status_label.config(text="No Main Model set", foreground="red")

        # Prompt model status
        prompt_model_name = self.extractor.model_manager.prompt_model_name
        if prompt_model_name:
            self.prompt_model_status_label.config(text=f"Prompt: {prompt_model_name}", foreground="green")
        else:
            self.prompt_model_status_label.config(text="No Prompt Model set", foreground="red")


    def _set_model(self):
        model_type = self.model_type_var.get()
        model_name = self.model_name_var.get()
        api_key = self.api_key_var.get()
        inference_type = self.inference_type_var.get()
        attn_implementation = self.attn_implementation_var.get()
        move_to_gpu = self.move_to_gpu_var.get()

        if not model_name:
            messagebox.showerror("Error", "Model Name/Path cannot be empty.")
            return
        if model_type == "OpenAI" and not api_key:
            messagebox.showerror("Error", "API Key is required for OpenAI models.")
            return

        try:
            if self.config_mode == 'main':
                self.extractor.model_manager.set_model(
                    model_name=model_name, model_type=model_type, api_key=api_key, 
                    inference_type=inference_type, attn_implementation=attn_implementation, 
                    move_to_gpu=move_to_gpu
                )

                desc = "Main model"
            else:
                print("attention implementation: ", attn_implementation)
                self.extractor.model_manager.set_prompt_model(
                    model_name=model_name, model_type=model_type, api_key=api_key, 
                    inference_type=inference_type, attn_implementation=attn_implementation, 
                    move_to_gpu=move_to_gpu
                )
                desc = "Prompt model"
            
            self.app.status_var.set(f"{desc} set to: {model_name} ({model_type})")
            messagebox.showinfo("Success", f"{desc} configured successfully.")
            self._update_model_status_display() # Refresh status on successful set
            self.app.extractor_view.update_button_states()
            self.app.topics_view.update_improve_button_state()
        except Exception as e:
            self.app.status_var.set(f"Error setting {self.config_mode} model: {e}")
            messagebox.showerror("Model Error", f"Failed to set {self.config_mode} model: {e}")


    def _set_model_as_prompt_model(self):
        try:
            self.extractor.model_manager.set_model_as_prompt_model()
            self.app.status_var.set("Main model set as prompt model.")
            messagebox.showinfo("Success", "Main model set as prompt model successfully.")
            # else:
            #     self.app.status_var.set("Prompt model set as main model.")
            #     messagebox.showinfo("Success", "Prompt model set as main model successfully.")
            self._update_model_status_display() # Refresh status on successful set
            self.app.extractor_view.update_button_states()
            self.app.topics_view.update_improve_button_state()
        except Exception as e:
            self.app.status_var.set(f"Error setting {self.config_mode} model as prompt model: {e}")
            messagebox.showerror("Model Error", f"Failed to set {self.config_mode} model as prompt model: {e}")

