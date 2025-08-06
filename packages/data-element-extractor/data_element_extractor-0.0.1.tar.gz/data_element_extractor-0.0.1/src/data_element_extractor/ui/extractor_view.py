import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv
from ..table_extractor import extract_from_csv_file
from ..config import config

import threading

class ExtractorView:
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.extractor = app.extractor

        self._create_extraction_ui(parent_frame)
        self.update_button_states()

    def _create_extraction_ui(self, parent_frame):
        extraction_frame = ttk.LabelFrame(parent_frame, text="Extraction Tasks", padding="10")
        extraction_frame.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)

        # Single Text Extraction
        single_text_frame = ttk.Frame(extraction_frame)
        single_text_frame.pack(fill=tk.X, pady=5)

        ttk.Label(single_text_frame, text="Text to Extract From:").pack(side=tk.LEFT, padx=(0, 5))
        self.text_input_area = tk.Text(single_text_frame, height=3, width=60)
        self.text_input_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)



        self.extract_text_button = ttk.Button(single_text_frame, text="Extract Data", command=self._extract_from_single_text)
        self.extract_text_button.pack(side=tk.LEFT, padx=5)


        # Progress Bar
        self.progress_bar = ttk.Progressbar(extraction_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 5))
        self.progress_bar.pack_forget() # Hide it initially


        # CSV Extraction
        csv_frame = ttk.Frame(extraction_frame)
        csv_frame.pack(fill=tk.X, pady=5)

        self.csv_evaluation_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(csv_frame, text="Include Evaluation", variable=self.csv_evaluation_var).pack(side=tk.LEFT, padx=5)

        ttk.Label(csv_frame, text="Batch Size:").pack(side=tk.LEFT, padx=(10, 0))
        self.batch_size_var = tk.StringVar(value="100")
        self.batch_size_entry = ttk.Entry(csv_frame, textvariable=self.batch_size_var, width=5)
        self.batch_size_entry.pack(side=tk.LEFT, padx=5)

        self.extract_csv_button = ttk.Button(csv_frame, text="Load CSV & Extract", command=self._load_and_extract_from_csv)
        self.extract_csv_button.pack(side=tk.LEFT, padx=5)

        # Results Display Area
        results_frame = ttk.Frame(extraction_frame)
        results_frame.pack(fill=tk.X, pady=5)
        ttk.Label(results_frame, text="Results:").pack(anchor=tk.W)
        self.results_display_area = tk.Text(results_frame, height=5, width=80, state=tk.DISABLED)
        self.results_display_area.pack(fill=tk.X, expand=True)



    def update_button_states(self):
        # A non-empty string for the main model name means a model is set.
        main_model_exists = bool(self.extractor.model_manager.model_name)
        state = tk.NORMAL if main_model_exists else tk.DISABLED
        self.extract_text_button.config(state=state)
        self.extract_csv_button.config(state=state)
        






    def _extract_from_single_text(self):
        text_to_extract = self.text_input_area.get("1.0", tk.END).strip()
        if not text_to_extract:
            messagebox.showwarning("Input Error", "Please enter text to extract from.")
            return
        if not self.extractor.get_topics():
            messagebox.showwarning("Setup Error", "No topics defined. Please add topics before extracting.")
            return

        try:
            extractions, probabilities = self.extractor.extract(text_to_extract, is_single_extraction=False, constrained_output=config.get_constrained_output_config())
            self.results_display_area.config(state=tk.NORMAL)
            self.results_display_area.delete("1.0", tk.END)
            if not extractions:
                self.results_display_area.insert(tk.END, "No extractions could be made (e.g., all topics skipped due to conditions).")
            else:
                result_text = f'Input: "{text_to_extract}"\n\n'
                for i, topic_info in enumerate(self.extractor.get_topics()):
                    topic_name = topic_info['topic_input'].value
                    if i < len(extractions):
                        extracted_value = extractions[i]
                        probability = probabilities[i] if i < len(probabilities) else "N/A"
                        prob_str = f"{probability:.4f}" if isinstance(probability, float) else str(probability)
                        
                        if extracted_value is not None:
                            result_text += f"{topic_name}: {extracted_value} (Confidence: {prob_str})\n"
                        else:
                            result_text += f"{topic_name}: [SKIPPED OR NO RESULT]\n"
                    else:
                        result_text += f"{topic_name}: [NOT PROCESSED]\n"
                self.results_display_area.insert(tk.END, result_text)

            self.results_display_area.config(state=tk.DISABLED)
            self.app.status_var.set("Extraction complete.")
        except Exception as e:
            messagebox.showerror("Extraction Error", f"An error occurred during extraction: {e}")
            self.app.status_var.set(f"Extraction error: {e}")






    def _load_and_extract_from_csv(self):
        if not self.extractor.get_topics():
            messagebox.showwarning("Setup Error", "No topics defined. Please add topics before extracting from a CSV.")
            return

        try:
            batch_size = int(self.batch_size_var.get())
            if batch_size <= 0:
                messagebox.showwarning("Input Error", "Batch size must be a positive integer.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Batch size must be a valid integer.")
            return

        csv_path = filedialog.askopenfilename(
            title="Select CSV File for Extraction",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not csv_path:
            return

        try:
            self.app.status_var.set(f"Starting CSV extraction for {os.path.basename(csv_path)}...")
            self.results_display_area.config(state=tk.NORMAL)
            self.results_display_area.delete("1.0", tk.END)
            self.results_display_area.insert(tk.END, f"Processing {os.path.basename(csv_path)}...\nOutput will be saved to a new file ending with '_result.csv'.\nCheck console for detailed progress.")
            self.results_display_area.config(state=tk.DISABLED)
            self.app.root.update_idletasks() # Ensure UI updates before blocking call

            # Progress bar handling
            self.progress_bar.pack(fill=tk.X, expand=True, padx=10, pady=(5, 0))
            self.progress_bar['value'] = 0
            self.app.root.update_idletasks()

            def progress_callback(current, total):
                progress = (current / total) * 100
                self.progress_bar['value'] = progress
                self.app.status_var.set(f"Processing row {current}/{total}...")
                self.app.root.update_idletasks()

            # Call the table classifier function with the progress callback
            extract_from_csv_file(
                dataset_path=csv_path,
                extractor_instance=self.extractor,
                with_evaluation=self.csv_evaluation_var.get(),
                constrained_output=config.get_constrained_output_config(),
                progress_callback=progress_callback,
                batch_size=batch_size
            )

            self.progress_bar.pack_forget() # Hide after completion

            result_message = f"CSV extraction finished for {os.path.basename(csv_path)}.\nResults saved to a file ending with '_result.csv' in the same directory."

            # If evaluation was done, read results and display them in the UI
            if self.csv_evaluation_var.get():
                base_name, _ = os.path.splitext(csv_path)
                result_csv_path = base_name + "_(result).csv"
                try:
                    with open(result_csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter=';')
                        evaluation_lines = []
                        found_header = False
                        for row in reader:
                            if not row: # Skip empty rows
                                continue
                            if row and row[0] == "Topic":
                                found_header = True
                            if found_header:
                                evaluation_lines.append(row)
                    
                    if evaluation_lines:
                        headers = evaluation_lines[0]
                        data_rows = evaluation_lines[1:]
                        
                        display_text = "\n\n--- Evaluation Results ---\n"
                        
                        for row in data_rows:
                            # Handle Elapsed Time row, which might not have a full set of values
                            if row and row[0] == "Elapsed Time":
                                display_text += f"\n{row[0]}: {row[1]}\n"
                                continue
                            
                            # It's a topic row
                            if not row or not row[0]: continue # Skip empty or malformed rows
                            topic_name = row[0]
                            display_text += f"\n--- Topic: {topic_name} ---\n"
                            
                            # Pair headers with values for this topic
                            for i in range(1, len(row)):
                                if i < len(headers): # Safety check
                                    header = headers[i]
                                    value = row[i]
                                    display_text += f"  {header}: {value}\n"
                        
                        self.results_display_area.config(state=tk.NORMAL)
                        self.results_display_area.insert(tk.END, display_text)
                        self.results_display_area.config(state=tk.DISABLED)
                        result_message += "\nEvaluation results also displayed below."

                except Exception as e:
                    result_message += f"\nCould not read and display evaluation results: {e}"

            messagebox.showinfo("CSV Extraction Complete", result_message)
            self.app.status_var.set("CSV extraction complete.")
        except Exception as e:
            messagebox.showerror("CSV Extraction Error", f"An error occurred: {e}")
            self.app.status_var.set(f"CSV extraction error: {e}")
            self.results_display_area.config(state=tk.NORMAL)
            self.results_display_area.insert(tk.END, f"\nError during CSV processing: {e}")
            self.results_display_area.config(state=tk.DISABLED)
            