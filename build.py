#!/usr/bin/env python3
import os
import subprocess
import sys

import wordfreq

if __name__ == "__main__":
    wordfreq_path = os.path.dirname(wordfreq.__file__)
    data_path = os.path.join(wordfreq_path, "data")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name=Fixibake",
        "--collect-all=wordfreq",
        "--collect-all=jieba",
        "--collect-all=ipadic",
        "--collect-all=mecab",
        "src/main.py",
    ]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)
