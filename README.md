# Fixibake

🌠 A GUI tool for fixing garbled CJK encodings in ZIP files and text files

## ✨ Features

- **Drag & Drop**: Simply drag ZIP or text files onto the application window
- **CJK Encoding Selection**: Select from a list of CJK encodings with confidence scores
- **Live Preview**: Preview filename corrections before extraction
- **One-Click Extract**: Extract files with correct encoding to selected directory
- **Text File Support**: Also supports fixing encoding in text files

## 🚀 Usage

1. Download the latest release from [GitHub Releases](https://github.com/uigleki/Fixibake/releases/latest)
2. Extract the ZIP file and run `Fixibake.exe`
3. Drag and drop a ZIP file or text file with garbled CJK characters into the window
4. Select the appropriate CJK encoding from the dropdown menu
5. Preview the corrected filenames
6. Click extract to decompress with proper encoding

## 🛠️ Development

Built with Python 3.11 using:

- **tkinter** - GUI framework
- **wordfreq** - CJK character frequency analysis
- **tkinterdnd2** - Drag and drop support
- **pyinstaller** - Executable packaging

### Building from source

```bash
# Install dependencies
pip install -e .

# Run from source
python src/main.py

# Build executable
python build.py
```

## 📄 License

[AGPL-3.0](LICENSE)
