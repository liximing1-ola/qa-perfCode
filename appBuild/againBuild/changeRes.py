#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK 资源替换工具
"""
import argparse
import shutil
import sys
from pathlib import Path


# 必需的资源文件
REQUIRED_FILES = {
    '72.png', '96.png', '144.png', '192.png', '432.png',
    '512.png', '1080.png', '1080.webp', 'login_btn.png', 'logo.png'
}

# 资源映射: (源文件名, 目标子路径, 目标文件名)
RESOURCE_MAPPINGS = [
    ('72.png', 'res/mipmap-hdpi', 'ic_launcher.png'),
    ('96.png', 'res/mipmap-xhdpi', 'ic_launcher.png'),
    ('144.png', 'res/mipmap-xxhdpi', 'ic_launcher.png'),
    ('192.png', 'res/mipmap-xxxhdpi', 'ic_launcher.png'),
    ('1080.png', 'res/mipmap-xxhdpi', 'splash.png'),
    ('512.png', 'res/drawable', 'ic_launcher.png'),
    ('144.png', 'assets/flutter_assets/assets/module/bbcore', 'logo.png'),
    ('432.png', 'res/drawable', 'ic_launcher_foreground.png'),
    ('432.png', 'res/mipmap-xxxhdpi', 'ic_launcher_foreground.png'),
    ('1080.webp', 'assets/flutter_assets/assets/module/login', 'login_splash.webp'),
    ('logo.png', 'res/drawable', 'logo.png'),
    ('login_btn.png', 'res/drawable', 'login_btn.png'),
]


def check_resources(res_dir: Path) -> None:
    """检查资源文件是否完整
    
    :param res_dir: 资源目录
    :raises EnvironmentError: 文件不完整时抛出
    """
    actual_files = {f.name for f in res_dir.iterdir() if f.is_file()}
    
    if actual_files == REQUIRED_FILES:
        return
    
    missing = REQUIRED_FILES - actual_files
    extra = actual_files - REQUIRED_FILES
    errors = []
    
    if missing:
        errors.append(f"缺少文件: {', '.join(missing)}")
    if extra:
        errors.append(f"多余文件: {', '.join(extra)}")
    
    raise EnvironmentError('; '.join(errors))


def copy_resource(src_dir: Path, dst_dir: Path, src_name: str, dst_name: str) -> None:
    """复制单个资源文件
    
    :param src_dir: 源目录
    :param dst_dir: 目标目录
    :param src_name: 源文件名
    :param dst_name: 目标文件名
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    src_file = src_dir / src_name
    dst_file = dst_dir / dst_name
    shutil.copy2(src_file, dst_file)
    print(f"Copied: {src_name} -> {dst_dir}/{dst_name}")


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='APK Resource Replacer')
    parser.add_argument('res_path', type=Path, help='APK 资源目录')
    parser.add_argument('res_name_path', type=Path, help='新资源目录')
    args = parser.parse_args()
    
    # 验证目录
    if not args.res_path.exists():
        print(f"Error: Resource path not found: {args.res_path}")
        return 1
    
    if not args.res_name_path.exists():
        print(f"Error: Source resource path not found: {args.res_name_path}")
        return 1
    
    try:
        # 检查资源完整性
        check_resources(args.res_name_path)
        
        # 复制资源
        for src_name, dst_subpath, dst_name in RESOURCE_MAPPINGS:
            dst_dir = args.res_path / dst_subpath
            copy_resource(args.res_name_path, dst_dir, src_name, dst_name)
        
        print("\nResource replacement completed!")
        return 0
        
    except EnvironmentError as e:
        print(f"Resource check failed: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
