#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 APK 基本信息
Usage: python getAppInfo.py <apk_path>
"""
import re
import subprocess
import sys
from pathlib import Path

AAPT_PATH = r'D:/build-tools/build-tools/29.0.2/aapt.exe'
PACKAGE_PATTERN = re.compile(r"package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'")


def get_apk_info(apk_path: str) -> dict:
    """获取 APK 包名、版本号、版本名称"""
    cmd = [AAPT_PATH, "dump", "badging", apk_path]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode != 0:
        raise RuntimeError(f"aapt 执行失败: {result.stderr}")
    
    match = PACKAGE_PATTERN.search(result.stdout)
    if not match:
        raise ValueError(f"无法解析包信息\n输出: {result.stdout[:500]}")
    
    return {
        'package': match.group(1),
        'version_code': match.group(2),
        'version_name': match.group(3)
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    apk_path = sys.argv[1]
    if not Path(apk_path).exists():
        print(f"APK 文件不存在: {apk_path}")
        return 1

    try:
        info = get_apk_info(apk_path)
        print(f"包名：{info['package']}")
        print(f"版本号：{info['version_code']}")
        print(f"版本名称：{info['version_name']}")
        return 0
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
