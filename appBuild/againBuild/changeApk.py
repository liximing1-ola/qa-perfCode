#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""APK 解包/打包工具 (使用 apktool)"""
import argparse
import subprocess
import sys
from pathlib import Path

APKTOOL = "apktool_3.0.1.jar"


def decompile(apk_path: Path) -> int:
    """解包 APK"""
    if not apk_path.exists():
        print(f"错误：文件不存在：{apk_path}")
        return 1

    cmd = ["java", "-jar", APKTOOL, "d", "-a", str(apk_path)]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"解包完成：{apk_path}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"解包失败：{e.stderr}")
        return e.returncode


def compile(source_dir: Path, output_apk: Path | None = None) -> int:
    """打包 APK"""
    if not source_dir.exists():
        print(f"错误：目录不存在：{source_dir}")
        return 1

    if output_apk is None:
        output_apk = Path(f"{source_dir}.apk")

    print(f"输出路径：{output_apk}")
    cmd = ["java", "-jar", APKTOOL, "b", str(source_dir), "-c", "-o", str(output_apk)]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"打包完成：{output_apk}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"打包失败：{e.stderr}")
        return e.returncode


def interactive_mode(target: Path) -> int:
    """交互模式"""
    print(f"目标：{target}")
    print("1. 解包 (Decompile)")
    print("2. 打包 (Compile)")
    print("0. 退出")
    choice = input("请选择操作：").strip()

    if choice == "1":
        return decompile(target)
    elif choice == "2":
        return compile(target)
    elif choice == "0":
        return 0
    else:
        print("无效选项，请输入 0、1 或 2")
        return 1


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='APK 解包/打包工具 (apktool)')
    parser.add_argument('target', type=Path, help='APK 文件或目录路径')
    parser.add_argument('-d', '--decompile', action='store_true', help='解包模式')
    parser.add_argument('-c', '--compile', action='store_true', help='打包模式')
    parser.add_argument('-o', '--output', type=Path, help='输出路径')
    args = parser.parse_args()

    # 自动检测模式
    if args.decompile:
        return decompile(args.target)
    elif args.compile:
        return compile(args.target, args.output)
    else:
        # 交互模式
        return interactive_mode(args.target)


if __name__ == '__main__':
    sys.exit(main())