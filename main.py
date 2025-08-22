import re
from typing import List, Optional, Tuple

from wordfreq import zipf_frequency

CJK_PATTERN = r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\uac00-\ud7af]"
DEFAULT_ENCODINGS = ["utf-8", "gbk", "big5", "shift_jis", "euc-jp", "euc-kr"]


def calculate_cjk_score(text: str) -> float:
    """Calculate naturalness score for CJK text based on character frequencies.

    Extracts CJK characters and computes the maximum average zipf frequency
    across Chinese, Japanese, and Korean language models.

    Args:
        text: Input text to analyze

    Returns:
        Naturalness score (0.0 if no CJK characters found)
    """
    cjk_chars = re.findall(CJK_PATTERN, text)
    if not cjk_chars:
        return 0.0

    zh_score = sum(zipf_frequency(char, "zh") for char in cjk_chars) / len(cjk_chars)
    ja_score = sum(zipf_frequency(char, "ja") for char in cjk_chars) / len(cjk_chars)
    ko_score = sum(zipf_frequency(char, "ko") for char in cjk_chars) / len(cjk_chars)

    return max(zh_score, ja_score, ko_score)


def detect_encoding(
    byte_data: bytes, encodings: Optional[List[str]] = None
) -> List[Tuple[str, str, float]]:
    """Detect the correct encoding for CJK byte data.

    Attempts to decode the byte data using various CJK encodings and scores
    each result based on text naturalness. Failed decodings receive a score of -1.

    Args:
        byte_data: Raw bytes to decode
        encodings: List of encodings to try (defaults to common CJK encodings)

    Returns:
        List of tuples (encoding, decoded_text, score) sorted by score descending.
        Failed decodings have decoded_text="DecodeError" and score=-1.
    """
    if encodings is None:
        encodings = DEFAULT_ENCODINGS

    results = []
    for encoding in encodings:
        try:
            decoded_text = byte_data.decode(encoding)
            score = calculate_cjk_score(decoded_text)
        except UnicodeDecodeError:
            decoded_text = "DecodeError"
            score = -1

        results.append((encoding, decoded_text, score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results
