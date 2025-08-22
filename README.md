# Fixibake

🌠 Fix garbled CJK filenames with intelligent encoding detection

## ✨ Features

- **Smart Detection**: Combines all filenames for improved encoding accuracy
- **Multiple Candidates**: Shows top 3 encoding possibilities with preview
- **Interactive Selection**: User-friendly interface when confidence is low
- **Batch Processing**: Handles entire ZIP archives or directories at once
- **CJK Optimized**: Specifically tuned for Chinese, Japanese, and Korean encodings

## 🚀 Usage

```bash
git clone https://github.com/uigleki/fixibake.git
cd fixibake
pip install -r requirements.txt


# Fix a ZIP file
python fixibake.py corrupted.zip

# Interactive mode for low confidence cases
python fixibake.py --interactive mixed_encoding.zip

# Process a directory
python fixibake.py --directory /path/to/garbled/files
```

## 📄 License

[AGPL-3.0](LICENSE)
