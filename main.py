import re
import zipfile
from statistics import fmean
from typing import List, Optional, Tuple

from wordfreq import zipf_frequency

CJK_PATTERN = re.compile(
    r"[\u3040-\u309f\u30a0-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]"
)
DEFAULT_ENCODINGS = ["utf-8", "gbk", "big5", "shift_jis", "euc-jp", "euc-kr"]


def score_cjk_text(text: str, limit: int = 10000) -> Tuple[float, str]:
    """Return a naturalness score for CJK text based on character frequency."""
    cjk_chars = CJK_PATTERN.findall(text)[:limit]
    if not cjk_chars:
        return 0.0, ""

    scores = {
        lang: fmean(zipf_frequency(ch, lang) for ch in cjk_chars)
        for lang in ("zh", "ja", "ko")
    }
    return max(scores.values()), "".join(cjk_chars)


def detect_zip_filename_encoding(
    file_path: str, encodings: Optional[List[str]] = None
) -> List[Tuple[str, float, str]]:
    """Detect filename encoding of a ZIP archive by scoring decoded text."""
    encodings = encodings or DEFAULT_ENCODINGS
    results: List[Tuple[str, float, str]] = []

    for encoding in encodings:
        try:
            with zipfile.ZipFile(file_path, "r", metadata_encoding=encoding) as zf:
                filenames = "".join(info.filename for info in zf.infolist())
                score, text = score_cjk_text(filenames)
                results.append((encoding, score, text))
        except (UnicodeError, OSError):
            results.append((encoding, -1.0, "DecodeError"))

    return sorted(results, key=lambda x: x[1], reverse=True)


def detect_zip_encoding(file_path: str):
    """Detect the best encoding for filenames in a ZIP archive."""
    results = detect_zip_filename_encoding(file_path)

    for enc, score, text in results:
        print(f"{enc:10} {score:.4f} {text[:50]}...")

    best = results[0]
    second_best = results[1]
    print(
        f"Best: {best[0]}, score: {best[1]:.4f}, delta: {best[1] - second_best[1]:.4f}"
    )


detect_zip_encoding("test.zip")
