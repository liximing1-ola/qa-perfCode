#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK 解包/打包工具 (使用 apktool)
"""
import argparse
import subprocess
import sys
from pathlib import Path

APKTOOL = "apktool_3.0.1.jar"


def decompile(apk_path: Path) -> int:
    """解包 APK
    
    :param apk_path: APK 文件路径
    :return: 命令返回码
    """
    if not apk_path.exists():
        print(f"Error: File not found: {apk_path}")
        return 1
    
    cmd = ["java", "-jar", APKTOOL, "d", "--only-main-classes", str(apk_path)]
    return subprocess.call(cmd)


def compile(source_dir: Path, output_apk: Path | None = None) -> int:
    """打包 APK
    
    :param source_dir: 源代码目录
    :param output_apk: 输出 APK 路径
    :return: 命令返回码
    """
    if not source_dir.exists():
        print(f"Error: Directory not found: {source_dir}")
        return 1
    
    if output_apk is None:
        output_apk = Path(f"{source_dir}.apk")
    
    print(f"Output: {output_apk}")
    cmd = ["java", "-jar", APKTOOL, "b", str(source_dir), "-c", "-o", str(output_apk)]
    return subprocess.call(cmd)


def interactive_mode(target: Path) -> int:
    """交互模式
    
    :param target: 目标路径
    :return: 返回码
    """
    print(f"Target: {target}")
    print("1. Decompile (解包)")
    print("2. Compile (打包)")
    choice = input("Select option: ").strip()
    
    if choice == "1":
        return decompile(target)
    elif choice == "2":
        return compile(target)
    else:
        print("Invalid option")
        return 1


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='APK Decompile/Compile Tool')
    parser.add_argument('target', type=Path, help='APK file or directory path')
    parser.add_argument('-d', '--decompile', action='store_true', help='Decompile mode')
    parser.add_argument('-c', '--compile', action='store_true', help='Compile mode')
    parser.add_argument('-o', '--output', type=Path, help='Output path')
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
