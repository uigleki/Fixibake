#!/usr/bin/env python3
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

from encoding_utils import detect_file_encoding, is_text_file

PREVIEW_LENGTH = 50
INVALID_FILE_MSG = "Please select a ZIP or text file"


class FixibakeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Fixibake - ZIP Encoding Fixer")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)

        self.file_path: Path | None = None
        self.encoding_results: list[tuple[str, float, str]] = []
        self.is_zip = False

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
        drop_frame = ttk.LabelFrame(parent, text="File", padding="10")
        drop_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        drop_frame.columnconfigure(0, weight=1)

        self.drop_label = tk.Label(
            drop_frame,
            text="Drag and drop file here or click to browse",
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

        self.extract_path = tk.StringVar(value=str(Path.cwd()))
        self.path_entry = ttk.Entry(path_frame, textvariable=self.extract_path)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_btn = ttk.Button(
            path_frame, text="Browse", command=self.browse_extract_path
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

        self.encoding_tree.column("encoding", width=80, stretch=False)
        self.encoding_tree.column("score", width=60, stretch=False)
        self.encoding_tree.column("preview", width=300, minwidth=200, stretch=True)

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
            command=self.extract_file,
            state="disabled",
        )
        self.extract_btn.grid(row=3, column=0, pady=10)

    def setup_drag_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event: tk.Event):
        files = self.root.tk.splitlist(event.data)
        if files:
            self.load_file(Path(files[0]))
        else:
            messagebox.showerror("Error", INVALID_FILE_MSG)

    def browse_file(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Supported files", "*.zip;*.txt"), ("All files", "*.*")],
        )
        if file_path:
            self.load_file(Path(file_path))

    def browse_extract_path(self):
        folder = filedialog.askdirectory(title="Select extract location")
        if folder:
            self.extract_path.set(folder)

    def load_file(self, file_path: Path):
        self.is_zip = file_path.suffix.lower() == ".zip"
        if not self.is_zip and not is_text_file(file_path):
            messagebox.showerror("Error", INVALID_FILE_MSG)
            return

        self.file_path = file_path
        self.drop_label.config(text=f"Loaded: {file_path.name}")

        extract_path = (
            file_path.with_suffix("")
            if self.is_zip
            else file_path.with_stem(file_path.stem + "_fixed")
        )
        self.extract_path.set(str(extract_path))

        self.detect_and_display_encodings()

    def detect_and_display_encodings(self):
        self.encoding_tree.delete(*self.encoding_tree.get_children())
        self.root.config(cursor="wait")
        self.root.update()

        self.encoding_results = detect_file_encoding(self.file_path)

        for encoding, score, preview in self.encoding_results:
            self.encoding_tree.insert(
                "", "end", values=(encoding, f"{score:.4f}", preview[:PREVIEW_LENGTH])
            )

        if self.encoding_tree.get_children():
            self.encoding_tree.selection_set(self.encoding_tree.get_children()[0])
            self.extract_btn.config(state="normal")

        self.root.config(cursor="")

    def extract_file(self):
        selection = self.encoding_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an encoding")
            return

        selected_encoding = self.encoding_results[
            self.encoding_tree.index(selection[0])
        ][0]
        extract_path_str = self.extract_path.get().strip()
        if not extract_path_str:
            messagebox.showerror("Error", "Please specify extract location")
            return

        extract_path = Path(extract_path_str)
        self.set_processing_state(True)

        try:
            if self.is_zip:
                self.extract_zip_file(extract_path, selected_encoding)
            else:
                self.convert_text_file(extract_path, selected_encoding)
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {e}")
        finally:
            self.set_processing_state(False)

    def set_processing_state(self, processing: bool):
        cursor = "wait" if processing else ""
        btn_state = "disabled" if processing else "normal"
        btn_text = "Processing..." if processing else "Extract with Selected Encoding"

        self.root.config(cursor=cursor)
        self.extract_btn.config(state=btn_state, text=btn_text)
        self.root.update()

    def extract_zip_file(self, extract_path: Path, encoding: str):
        extract_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.file_path, "r", metadata_encoding=encoding) as zf:
            zf.extractall(extract_path)
        messagebox.showinfo(
            "Success", f"ZIP extracted to: {extract_path}\nUsing encoding: {encoding}"
        )

    def convert_text_file(self, extract_path: Path, encoding: str):
        with open(self.file_path, "r", encoding=encoding, errors="ignore") as f:
            content = f.read()
        with open(extract_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo(
            "Success", f"Text converted to: {extract_path}\nFrom encoding: {encoding}"
        )


def main():
    root = TkinterDnD.Tk()
    FixibakeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
