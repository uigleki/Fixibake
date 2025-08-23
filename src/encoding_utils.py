import re
import zipfile
from pathlib import Path
from statistics import fmean

import magic
from wordfreq import zipf_frequency

CJK_PATTERN = re.compile(
    r"[\u3040-\u309f\u30a0-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]"
)
ZIPF_LANGUAGES = ("zh", "ja", "ko")

DEFAULT_ENCODINGS = ("utf-8", "gbk", "big5", "shift_jis", "euc-jp", "euc-kr")

_FILE_LIMIT = 1_000
_CJK_LIMIT = 10_000


def is_text_file(file_path: str | Path) -> bool:
    """Check if a file is a text file based on its MIME type."""
    return magic.from_file(file_path, mime=True).startswith("text/")


def score_cjk_text(text: str, limit: int = _CJK_LIMIT) -> tuple[float, str]:
    """Return a naturalness score for CJK text based on character frequency."""
    cjk_chars = CJK_PATTERN.findall(text)[:limit]
    if not cjk_chars:
        return 0.0, ""

    try:
        scores = {
            lang: fmean(zipf_frequency(ch, lang) for ch in cjk_chars)
            for lang in ZIPF_LANGUAGES
        }
        return max(scores.values()), "".join(cjk_chars)
    except FileNotFoundError:
        return -1, "FileNotFoundError"


def detect_file_encoding(
    file_path: str | Path, encodings: tuple[str, ...] | None = None
) -> list[tuple[str, float, str]]:
    """Detect file encoding by scoring decoded content for both ZIP and text files."""
    path = Path(file_path)
    encodings = encodings or DEFAULT_ENCODINGS
    results: list[tuple[str, float, str]] = []

    is_zip = zipfile.is_zipfile(path)

    if not is_zip and not is_text_file(path):
        raise ValueError(f"File is neither a ZIP file nor a text file: {path}")

    for encoding in encodings:
        content = ""
        try:
            if is_zip:
                with zipfile.ZipFile(path, "r", metadata_encoding=encoding) as zf:
                    content = "".join(
                        info.filename for info in zf.infolist()[:_FILE_LIMIT]
                    )
            else:
                with open(path, "r", encoding=encoding, errors="ignore") as f:
                    content = f.read(10240)

        except (UnicodeError, OSError):
            results.append((encoding, -1.0, "DecodeError"))
            continue

        score, text = score_cjk_text(content)
        results.append((encoding, score, text))

    return sorted(results, key=lambda x: x[1], reverse=True)
