#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取 APK 基本信息"""
import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path

# AAPT 路径配置（直接在此修改）
AAPT_PATH = Path(r'D:/build-tools/build-tools/29.0.2/aapt.exe')
PACKAGE_PATTERN = re.compile(
    r"package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'"
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AAPTError(Exception):
    """AAPT 执行异常"""


def get_apk_info(apk_path: Path, aapt_path: Path) -> dict[str, str]:
    """获取 APK 包名、版本号、版本名称"""
    if not apk_path.exists():
        raise FileNotFoundError(f"APK 文件不存在：{apk_path}")

    if not aapt_path.exists():
        raise FileNotFoundError(f"AAPT 工具不存在：{aapt_path}")

    cmd = [str(aapt_path), "dump", "badging", str(apk_path)]
    logger.debug(f"执行命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        raise AAPTError(f"aapt 执行失败：{result.stderr}")

    match = PACKAGE_PATTERN.search(result.stdout)
    if not match:
        raise ValueError(f"无法解析包信息\n输出：{result.stdout[:500]}")

    return {
        'package': match.group(1),
        'version_code': match.group(2),
        'version_name': match.group(3)
    }


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='获取 APK 基本信息')
    parser.add_argument('apk', type=Path, help='APK 文件路径')
    parser.add_argument('-a', '--aapt', type=Path, default=AAPT_PATH,
                        help=f'AAPT 工具路径（默认：{AAPT_PATH}）')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='显示详细调试信息')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        info = get_apk_info(args.apk, args.aapt)
        print(f"包名：{info['package']}")
        print(f"版本号：{info['version_code']}")
        print(f"版本名称：{info['version_name']}")
        return 0

    except (FileNotFoundError, AAPTError, ValueError) as e:
        logger.error(f"{e}")
        return 1
    except Exception as e:
        logger.exception(f"未知错误：{e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
