#!/usr/bin/env python3
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

from encoding_utils import detect_zip_filename_encoding


class FixibakeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Fixibake - ZIP Encoding Fixer")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)

        self.zip_file_path: Path | None = None
        self.encoding_results: list[tuple[str, float, str]] = []

        self.setup_ui()
        self.setup_drag_drop()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.setup_drop_area(main_frame)
        self.setup_extract_path(main_frame)
        self.setup_encoding_list(main_frame)
        self.setup_extract_button(main_frame)

    def setup_drop_area(self, parent: ttk.Frame):
        drop_frame = ttk.LabelFrame(parent, text="ZIP File", padding="10")
        drop_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        drop_frame.columnconfigure(0, weight=1)

        self.drop_label = tk.Label(
            drop_frame,
            text="Drag and drop ZIP file here",
            bg="#f0f0f0",
            relief="sunken",
            height=3,
            font=("TkDefaultFont", 10),
        )
        self.drop_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.drop_label.bind("<Button-1>", self.browse_file)

    def setup_extract_path(self, parent: ttk.Frame):
        path_frame = ttk.LabelFrame(parent, text="Extract Location", padding="10")
        path_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)

        path_inner = ttk.Frame(path_frame)
        path_inner.grid(row=0, column=0, sticky=(tk.W, tk.E))
        path_inner.columnconfigure(0, weight=1)

        self.extract_path = tk.StringVar(value=str(Path.cwd()))
        self.path_entry = ttk.Entry(path_inner, textvariable=self.extract_path)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_btn = ttk.Button(
            path_inner, text="Browse", command=self.browse_extract_path
        )
        browse_btn.grid(row=0, column=1)

    def setup_encoding_list(self, parent: ttk.Frame):
        list_frame = ttk.LabelFrame(
            parent, text="Encoding Detection Results", padding="10"
        )
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("encoding", "score", "preview")
        self.encoding_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=8
        )

        self.encoding_tree.heading("encoding", text="Encoding")
        self.encoding_tree.heading("score", text="Score")
        self.encoding_tree.heading("preview", text="Preview")

        self.encoding_tree.column("encoding", width=100, minwidth=80)
        self.encoding_tree.column("score", width=80, minwidth=60)
        self.encoding_tree.column("preview", width=300, minwidth=200)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.encoding_tree.yview
        )
        self.encoding_tree.configure(yscrollcommand=scrollbar.set)

        self.encoding_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def setup_extract_button(self, parent: ttk.Frame):
        self.extract_btn = ttk.Button(
            parent,
            text="Extract with Selected Encoding",
            command=self.extract_zip,
            state="disabled",
        )
        self.extract_btn.grid(row=3, column=0, pady=10)

    def setup_drag_drop(self):
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event: tk.Event):
        files = self.root.tk.splitlist(event.data)
        if files and Path(files[0]).suffix.lower() == ".zip":
            self.load_zip_file(Path(files[0]))
        else:
            messagebox.showerror("Error", "Please drop a ZIP file")

    def browse_file(self, event: tk.Event | None = None):
        file_path = filedialog.askopenfilename(
            title="Select ZIP file", filetypes=[("ZIP files", "*.zip")]
        )
        if file_path:
            self.load_zip_file(Path(file_path))

    def browse_extract_path(self):
        folder = filedialog.askdirectory(title="Select extract location")
        if folder:
            self.extract_path.set(folder)

    def load_zip_file(self, file_path: Path):
        try:
            if not zipfile.is_zipfile(file_path):
                messagebox.showerror("Error", "Not a valid ZIP file")
                return

            self.zip_file_path = file_path
            self.drop_label.config(text=f"Loaded: {file_path.name}")

            auto_extract_path = file_path.parent / file_path.stem
            self.extract_path.set(str(auto_extract_path))

            self.encoding_tree.delete(*self.encoding_tree.get_children())

            self.root.config(cursor="wait")
            self.root.update()

            try:
                self.encoding_results = detect_zip_filename_encoding(file_path)

                for encoding, score, preview in self.encoding_results:
                    display_score = f"{score:.4f}" if score >= 0 else "Error"
                    preview_text = (
                        preview[:50]
                        if preview and preview != "DecodeError"
                        else "Decode failed"
                    )

                    self.encoding_tree.insert(
                        "", "end", values=(encoding, display_score, preview_text)
                    )

                if self.encoding_results:
                    first_item = self.encoding_tree.get_children()[0]
                    self.encoding_tree.selection_set(first_item)
                    self.extract_btn.config(state="normal")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to analyze ZIP file: {str(e)}")

            finally:
                self.root.config(cursor="")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ZIP file: {str(e)}")

    def extract_zip(self):
        if not self.zip_file_path or not self.encoding_results:
            messagebox.showerror("Error", "No ZIP file loaded")
            return

        selection = self.encoding_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an encoding")
            return

        selected_index = self.encoding_tree.index(selection[0])
        selected_encoding = self.encoding_results[selected_index][0]

        extract_path_str = self.extract_path.get().strip()
        if not extract_path_str:
            messagebox.showerror("Error", "Please specify extract location")
            return

        extract_path = Path(extract_path_str)
        if not extract_path.is_dir():
            try:
                extract_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create directory: {str(e)}")
                return

        try:
            self.root.config(cursor="wait")
            self.extract_btn.config(state="disabled", text="Extracting...")
            self.root.update()

            with zipfile.ZipFile(
                str(self.zip_file_path), "r", metadata_encoding=selected_encoding
            ) as zf:
                zf.extractall(str(extract_path))

            messagebox.showinfo(
                "Success",
                f"ZIP file extracted successfully to:\n{extract_path}\n\nUsing encoding: {selected_encoding}",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract ZIP file: {str(e)}")

        finally:
            self.root.config(cursor="")
            self.extract_btn.config(
                state="normal", text="Extract with Selected Encoding"
            )


def main():
    root = TkinterDnD.Tk()
    FixibakeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
