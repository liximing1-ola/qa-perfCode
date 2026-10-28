#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK 资源替换工具
"""
import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


# 必需的资源文件
REQUIRED_FILES = {
    '72.png', '96.png', '144.png', '192.png', '432.png',
    '512.png', '1080.png', '1080.webp', 'login_btn.png', 'logo.png'
}


@dataclass(frozen=True)
class ResourceMapping:
    """资源映射配置"""
    src_name: str       # 源文件名
    dst_subpath: str    # 目标子路径
    dst_name: str       # 目标文件名


# 资源映射列表（使用 dataclass 增强可读性）
RESOURCE_MAPPINGS = [
    ResourceMapping('72.png', 'res/mipmap-hdpi', 'ic_launcher.png'),
    ResourceMapping('96.png', 'res/mipmap-xhdpi', 'ic_launcher.png'),
    ResourceMapping('144.png', 'res/mipmap-xxhdpi', 'ic_launcher.png'),
    ResourceMapping('192.png', 'res/mipmap-xxxhdpi', 'ic_launcher.png'),
    ResourceMapping('1080.png', 'res/mipmap-xxhdpi', 'splash.png'),
    ResourceMapping('512.png', 'res/drawable', 'ic_launcher.png'),
    ResourceMapping('144.png', 'assets/flutter_assets/assets/module/bbcore', 'logo.png'),
    ResourceMapping('432.png', 'res/drawable', 'ic_launcher_foreground.png'),
    ResourceMapping('432.png', 'res/mipmap-xxxhdpi', 'ic_launcher_foreground.png'),
    ResourceMapping('1080.webp', 'assets/flutter_assets/assets/module/login', 'login_splash.webp'),
    ResourceMapping('logo.png', 'res/drawable', 'logo.png'),
    ResourceMapping('login_btn.png', 'res/drawable', 'login_btn.png'),
]


class ResourceError(Exception):
    """资源相关操作异常"""


def check_resources(res_dir: Path) -> None:
    """检查资源文件是否完整
    
    :param res_dir: 资源目录
    :raises ResourceError: 文件不完整时抛出
    """
    actual_files = {f.name for f in res_dir.iterdir() if f.is_file()}
    
    if actual_files == REQUIRED_FILES:
        return
    
    missing = REQUIRED_FILES - actual_files
    extra = actual_files - REQUIRED_FILES
    errors = []
    
    if missing:
        errors.append(f"缺少文件: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"多余文件: {', '.join(sorted(extra))}")
    
    raise ResourceError('; '.join(errors))


def copy_resource(src_dir: Path, dst_dir: Path, mapping: ResourceMapping) -> bool:
    """复制单个资源文件
    
    :param src_dir: 源目录
    :param dst_dir: 目标根目录
    :param mapping: 资源映射配置
    :return: 是否成功复制
    :raises ResourceError: 源文件不存在或复制失败时
    """
    src_file = src_dir / mapping.src_name
    
    # 验证源文件存在
    if not src_file.exists():
        raise ResourceError(f"源文件不存在: {src_file}")
    
    dst_subdir = dst_dir / mapping.dst_subpath
    dst_subdir.mkdir(parents=True, exist_ok=True)
    dst_file = dst_subdir / mapping.dst_name
    
    try:
        shutil.copy2(src_file, dst_file)
        print(f"✓ {mapping.src_name} -> {mapping.dst_subpath}/{mapping.dst_name}")
        return True
    except OSError as e:
        raise ResourceError(f"复制失败 {mapping.src_name}: {e}")


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='APK Resource Replacer')
    parser.add_argument('res_path', type=Path, help='APK 资源目录')
    parser.add_argument('res_name_path', type=Path, help='新资源目录')
    args = parser.parse_args()
    
    # 验证目录
    if not args.res_path.exists():
        print(f"错误: 资源目录不存在: {args.res_path}")
        return 1
    
    if not args.res_path.is_dir():
        print(f"错误: 资源路径不是目录: {args.res_path}")
        return 1
    
    if not args.res_name_path.exists():
        print(f"错误: 源资源目录不存在: {args.res_name_path}")
        return 1
    
    if not args.res_name_path.is_dir():
        print(f"错误: 源资源路径不是目录: {args.res_name_path}")
        return 1
    
    try:
        # 检查资源完整性
        print("正在检查资源文件...")
        check_resources(args.res_name_path)
        
        # 复制资源
        print(f"\n开始复制资源（共 {len(RESOURCE_MAPPINGS)} 个映射）...")
        success_count = 0
        for mapping in RESOURCE_MAPPINGS:
            copy_resource(args.res_name_path, args.res_path, mapping)
            success_count += 1
        
        print(f"\n资源替换完成！成功: {success_count}/{len(RESOURCE_MAPPINGS)}")
        return 0
        
    except ResourceError as e:
        print(f"\n资源操作失败: {e}")
        return 1
    except Exception as e:
        print(f"\n未知错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
