#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK 重新签名工具
支持通过命令行参数指定输入输出路径
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
from enum import Enum
from dataclasses import dataclass


class KeystoreType(Enum):
    """密钥库类型"""
    SLP = "slp"      # 不夜星球
    RBP = "rbp"      # 彩虹星球


@dataclass
class KeystoreConfig:
    """密钥库配置"""
    path: str
    password: str


# 预定义的密钥库配置
KEYSTORE_CONFIGS = {
    KeystoreType.SLP: KeystoreConfig(
        path=r'D:\keystore\slp.keystore',
        password='PLS_699'
    ),
    KeystoreType.RBP: KeystoreConfig(
        path=r'D:\keystore\rbp.keystore',
        password='634rbp'
    )
}

# 默认 SDK 路径
DEFAULT_SDK_PATH = r'D:/build-tools/build-tools/29.0.2/apksigner.bat'


def validate_file_exists(file_path: str, file_description: str) -> Path:
    """验证文件是否存在"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_description} not found: {file_path}")
    return path


def validate_sdk_path(sdk_path: str) -> Path:
    """验证 SDK 路径是否存在"""
    return validate_file_exists(sdk_path, "SDK path")


def build_sign_command(sdk_path: str, keystore: KeystoreConfig, 
                       apk_path: str, out_path: str) -> list:
    """构建签名命令"""
    return [
        sdk_path,
        'sign',
        '--ks', keystore.path,
        '--ks-pass', f'pass:{keystore.password}',
        '--out', out_path,
        apk_path
    ]


def build_verify_command(sdk_path: str, apk_path: str) -> list:
    """构建验证命令"""
    return [sdk_path, "verify", "-v", apk_path]


def execute_command(cmd: list, operation_name: str) -> None:
    """执行命令并处理错误"""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"{operation_name} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"{operation_name} failed: {e.stderr}") from e


def sign_apk(sdk_path: str, keystore: KeystoreConfig, 
             apk_path: str, out_path: str) -> None:
    """执行 APK 签名"""
    sign_cmd = build_sign_command(sdk_path, keystore, apk_path, out_path)
    execute_command(sign_cmd, "Signing")


def verify_apk(sdk_path: str, apk_path: str) -> None:
    """验证 APK 签名"""
    verify_cmd = build_verify_command(sdk_path, apk_path)
    execute_command(verify_cmd, "Verification")


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='APK Re-signing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python againKey.py input.apk output.apk
  python againKey.py input.apk output.apk --keystore rbp
  python againKey.py input.apk output.apk --sdk-path /path/to/apksigner
        """
    )
    parser.add_argument('input', help='输入 APK 文件路径')
    parser.add_argument('output', help='输出 APK 文件路径')
    parser.add_argument(
        '--keystore', 
        choices=[k.value for k in KeystoreType],
        default=KeystoreType.SLP.value,
        help='选择密钥库类型 (默认: slp)'
    )
    parser.add_argument(
        '--sdk-path',
        default=DEFAULT_SDK_PATH,
        help=f'SDK 路径 (默认: {DEFAULT_SDK_PATH})'
    )
    return parser.parse_args()


def main() -> int:
    """主函数"""
    try:
        args = parse_arguments()
        
        # 验证输入文件
        validate_file_exists(args.input, "Input APK")
        
        # 验证 SDK
        validate_sdk_path(args.sdk_path)
        
        # 获取密钥库配置
        keystore_type = KeystoreType(args.keystore)
        keystore = KEYSTORE_CONFIGS[keystore_type]
        
        # 确保输出目录存在
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 执行签名
        sign_apk(args.sdk_path, keystore, args.input, args.output)
        
        # 验证签名
        verify_apk(args.sdk_path, args.output)
        
        print('-----------------------sign-----------------------')
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
