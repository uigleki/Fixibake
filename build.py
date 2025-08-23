#!/usr/bin/env python3
import subprocess
import sys

if __name__ == "__main__":
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=Fixibake",
        "--collect-data=wordfreq",
        "--collect-data=jieba",
        "--collect-data=ipadic",
        "--collect-data=mecab_ko_dic",
        "src/main.py",
    ]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)
