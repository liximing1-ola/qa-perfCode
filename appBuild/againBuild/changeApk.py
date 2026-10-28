#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""APK 解包/打包工具 (使用 apktool)"""
import argparse
import logging
import subprocess
import sys
from pathlib import Path

APKTOOL = "apktool_3.0.1.jar"

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def decompile(apk_path: Path) -> int:
    """解包 APK"""
    if not apk_path.exists():
        logger.error(f"文件不存在：{apk_path}")
        return 1

    cmd = ["java", "-jar", APKTOOL, "d", "-a", str(apk_path)]
    logger.info(f"开始解包：{apk_path}")
    logger.debug(f"执行命令：{' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"解包完成：{apk_path}")
        if result.stdout:
            logger.debug(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        logger.error(f"解包失败：{e.stderr}")
        return e.returncode
    except FileNotFoundError:
        logger.error(f"找不到 Java 或 {APKTOOL}，请检查环境配置")
        return 1


def compile(source_dir: Path, output_apk: Path | None = None) -> int:
    """打包 APK"""
    if not source_dir.exists():
        logger.error(f"目录不存在：{source_dir}")
        return 1

    if not source_dir.is_dir():
        logger.error(f"路径不是目录：{source_dir}")
        return 1

    if output_apk is None:
        output_apk = Path(f"{source_dir}.apk")

    logger.info(f"输出路径：{output_apk}")
    cmd = ["java", "-jar", APKTOOL, "b", str(source_dir), "-c", "-o", str(output_apk)]
    logger.debug(f"执行命令：{' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"打包完成：{output_apk}")
        if result.stdout:
            logger.debug(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        logger.error(f"打包失败：{e.stderr}")
        return e.returncode
    except FileNotFoundError:
        logger.error(f"找不到 Java 或 {APKTOOL}，请检查环境配置")
        return 1


def interactive_mode(target: Path) -> int:
    """交互模式"""
    logger.info(f"目标：{target}")
    print("\n请选择操作：")
    print("  1. 解包 (Decompile)")
    print("  2. 打包 (Compile)")
    print("  0. 退出")
    
    try:
        choice = input("\n请输入选项 (0/1/2): ").strip()

        if choice == "1":
            return decompile(target)
        elif choice == "2":
            return compile(target)
        elif choice == "0":
            logger.info("退出")
            return 0
        else:
            logger.error("无效选项，请输入 0、1 或 2")
            return 1
    except KeyboardInterrupt:
        print()  # 换行
        logger.info("操作已取消")
        return 0
    except EOFError:
        logger.info("输入结束")
        return 0


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='APK 解包/打包工具 (apktool)')
    parser.add_argument('target', type=Path, help='APK 文件或目录路径')
    parser.add_argument('-d', '--decompile', action='store_true', help='解包模式')
    parser.add_argument('-c', '--compile', action='store_true', help='打包模式')
    parser.add_argument('-o', '--output', type=Path, help='输出路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细调试信息')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

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