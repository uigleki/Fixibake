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
        "--windowed",
        "--name=Fixibake",
        "--collect-all=wordfreq",
        "--collect-all=jieba",
        "--collect-all=ipadic",
        "--collect-all=mecab",
        f"--add-data={data_path}{os.pathsep}wordfreq/data",
        "src/main.py",
    ]

    print(f"data_path: {data_path}")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)
