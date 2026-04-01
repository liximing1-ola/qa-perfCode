#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 APK 基本信息

支持获取包名、版本号、版本名称等信息
"""
import re
import subprocess
import sys
from pathlib import Path

# AAPT 路径配置（可通过环境变量覆盖）
AAPT_PATH = Path(r'D:/build-tools/build-tools/29.0.2/aapt.exe')
PACKAGE_PATTERN = re.compile(
    r"package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'"
)


class AAPTError(Exception):
    """AAPT 执行异常"""
    pass


def get_apk_info(apk_path: Path) -> dict[str, str]:
    """获取 APK 包名、版本号、版本名称
    
    :param apk_path: APK 文件路径
    :return: APK 信息字典
    :raises AAPTError: AAPT 执行失败时
    :raises ValueError: 无法解析包信息时
    """
    if not apk_path.exists():
        raise FileNotFoundError(f"APK 文件不存在：{apk_path}")
    
    cmd = [str(AAPT_PATH), "dump", "badging", str(apk_path)]
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
    if len(sys.argv) < 2:
        print(__doc__)
        print("用法：python getAppInfo.py <apk_path>")
        return 1

    apk_path = Path(sys.argv[1])
    
    try:
        info = get_apk_info(apk_path)
        print(f"包名：{info['package']}")
        print(f"版本号：{info['version_code']}")
        print(f"版本名称：{info['version_name']}")
        return 0
        
    except FileNotFoundError as e:
        print(f"错误：{e}")
        return 1
    except AAPTError as e:
        print(f"AAPT 错误：{e}")
        return 1
    except Exception as e:
        print(f"未知错误：{e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
