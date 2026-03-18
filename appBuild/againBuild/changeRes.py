#!/usr/bin/env python3
import os
import shutil
import sys

REQUIRED_FILES = {'72.png', '96.png', '144.png', '192.png', '432.png',
                  '512.png', '1080.png', '1080.webp', 'login_btn.png', 'logo.png'}


def check_resources(res_name_path: str) -> None:
    """检查资源文件是否完整"""
    actual_files = set(os.listdir(res_name_path))
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


def copy_resource(src_dir: str, dst_dir: str, src_name: str, dst_name: str) -> None:
    """复制单个资源文件"""
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(os.path.join(src_dir, src_name), os.path.join(dst_dir, dst_name))
    print(f"Copied: {src_name} -> {dst_dir}/{dst_name}")


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: python changeRes.py <res_path> <res_name_path>')
        return 1

    res_path, res_name_path = sys.argv[1], sys.argv[2]
    pkg_res = os.path.join(res_path, 'res')
    module = os.path.join(res_path, 'assets', 'flutter_assets', 'assets', 'module')

    check_resources(res_name_path)

    # 资源映射: (源文件名, 目标目录, 目标文件名)
    resources = [
        ('72.png', f'{pkg_res}/mipmap-hdpi', 'ic_launcher.png'),
        ('96.png', f'{pkg_res}/mipmap-xhdpi', 'ic_launcher.png'),
        ('144.png', f'{pkg_res}/mipmap-xxhdpi', 'ic_launcher.png'),
        ('192.png', f'{pkg_res}/mipmap-xxxhdpi', 'ic_launcher.png'),
        ('1080.png', f'{pkg_res}/mipmap-xxhdpi', 'splash.png'),
        ('512.png', f'{pkg_res}/drawable', 'ic_launcher.png'),
        ('144.png', f'{module}/bbcore', 'logo.png'),
        ('432.png', f'{pkg_res}/drawable', 'ic_launcher_foreground.png'),
        ('432.png', f'{pkg_res}/mipmap-xxxhdpi', 'ic_launcher_foreground.png'),
        ('1080.webp', f'{module}/login', 'login_splash.webp'),
        ('logo.png', f'{pkg_res}/drawable', 'logo.png'),
        ('login_btn.png', f'{pkg_res}/drawable', 'login_btn.png'),
    ]

    try:
        for src_name, dst_dir, dst_name in resources:
            copy_resource(res_name_path, dst_dir, src_name, dst_name)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
