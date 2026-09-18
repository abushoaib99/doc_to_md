import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from markitdown import MarkItDown


class MarkItDownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MarkItDown Batch Converter")
        self.root.geometry("650x550")
        
        self.selected_files = []
        self.markitdown = MarkItDown()

        self.setup_ui()

    def setup_ui(self):
        # Header / Controls Frame
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)

        self.btn_select = ttk.Button(btn_frame, text="Upload Files", command=self.select_files)
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.btn_clear = ttk.Button(btn_frame, text="Clear Selection", command=self.clear_files)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # File List Display Box
        list_frame = ttk.LabelFrame(self.root, text=" Selected Files ", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Progress Bar Frame
        prog_frame = ttk.Frame(self.root, padding=10)
        prog_frame.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(prog_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # Convert Action Button
        self.btn_convert = ttk.Button(self.root, text="Convert to Markdown", command=self.start_conversion)
        self.btn_convert.pack(fill=tk.X, padx=10, pady=5)

        # Log Display Window
        log_frame = ttk.LabelFrame(self.root, text=" Logs ", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_box = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_box.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_box.config(yscrollcommand=log_scroll.set)

    def select_files(self):
        filetypes = (
            ("Supported Files", "*.pdf *.docx *.xlsx *.pptx *.png *.jpg *.jpeg *.html *.csv *.json *.xml"),
            ("All Files", "*.*")
        )
        files = filedialog.askopenfilenames(title="Select Documents to Convert", filetypes=filetypes)
        
        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_listbox.insert(tk.END, file_path)

    def clear_files(self):
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.progress_bar['value'] = 0
        
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state=tk.DISABLED)

    def log(self, message):
        """Append log message in thread-safe manner."""
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select at least one file to convert.")
            return

        # Disable UI controls during process
        self.btn_convert.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
        self.btn_clear.config(state=tk.DISABLED)

        self.log("Starting batch conversion...\n" + "-" * 40)
        self.progress_bar['value'] = 0

        # Run conversion in a separate thread so UI stays interactive
        threading.Thread(target=self.process_conversion, daemon=True).start()

    def process_conversion(self):
        successful = 0
        failed = 0
        total = len(self.selected_files)

        for index, file_path in enumerate(self.selected_files, start=1):
            file_name = os.path.basename(file_path)
            input_dir = os.path.dirname(file_path)
            
            # Create a 'markdown' folder inside the input file's directory
            output_dir = os.path.join(input_dir, "markdown")
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(file_name)[0]
            output_path = os.path.join(output_dir, f"{base_name}.md")

            try:
                # Core MarkItDown conversion
                result = self.markitdown.convert(file_path)

                # Save generated markdown content
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.text_content)

                successful += 1
                self.log(f"✓ Converted: {file_name} -> markdown/{base_name}.md")
            except Exception as e:
                failed += 1
                self.log(f"✗ Failed: {file_name} | Error: {str(e)}")

            # Update progress bar safely
            progress = (index / total) * 100
            self.root.after(0, self.update_progress, progress)

        self.root.after(0, self.conversion_complete, successful, failed)

    def update_progress(self, val):
        self.progress_bar['value'] = val

    def conversion_complete(self, successful, failed):
        # Re-enable UI components
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_select.config(state=tk.NORMAL)
        self.btn_clear.config(state=tk.NORMAL)

        self.log("-" * 40)
        self.log(f"Completed! Converted: {successful} | Failed: {failed}")
        messagebox.showinfo("Done", f"Conversion completed!\nSaved converted files in 'markdown' subfolders.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkItDownApp(root)
    root.mainloop()