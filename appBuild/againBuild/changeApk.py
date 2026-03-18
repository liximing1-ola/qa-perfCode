#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

APKTOOL = "apktool_2.6.1.jar"


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {Path(__file__).name} <file_path>")
        return 1

    target = sys.argv[1]
    choice = input("1=解包 2=打包: ").strip()

    if choice == "1":
        if not Path(target).exists():
            print(f"文件不存在: {target}")
            return 1
        cmd = f"java -jar {APKTOOL} d --only-main-classes {target}"
    elif choice == "2":
        if not Path(target).exists():
            print(f"文件夹不存在: {target}")
            return 1
        output = f"{target}.apk"
        print(f"输出: {output}")
        cmd = f"java -jar {APKTOOL} b {target} -c -o {output}"
    else:
        print("无效选项")
        return 1

    return os.system(cmd)


if __name__ == '__main__':
    sys.exit(main())
