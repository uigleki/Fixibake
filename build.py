#!/usr/bin/env python3
import shutil
import subprocess
import sys

if __name__ == "__main__":
    cmd = [
        "pyinstaller",
        "--windowed",
        "--name=Fixibake",
        "--collect-data=wordfreq",
        "--collect-data=jieba",
        "--collect-data=ipadic",
        "--collect-data=mecab_ko_dic",
        "src/main.py",
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        shutil.make_archive("dist/Fixibake", "zip", "dist", "Fixibake")

    sys.exit(result.returncode)
