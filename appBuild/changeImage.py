#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片批量转灰度工具
"""
import argparse
import sys
from pathlib import Path
from PIL import Image


# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}


def convert_image(input_path: Path, output_path: Path, quality: int = 95) -> bool:
    """转换单张图片为灰度
    
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param quality: JPEG 质量 (1-100)
    :return: 是否成功
    """
    try:
        with Image.open(input_path) as img:
            gray = img.convert('L')
            gray.save(output_path, quality=quality)
        return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False


def batch_convert(input_dir: Path, output_dir: Path) -> tuple[int, int]:
    """批量转换目录中的图片
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :return: (成功数, 总数)
    """
    # 查找所有图片
    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]
    
    total = len(image_files)
    if total == 0:
        print("No image files found")
        return 0, 0
    
    print(f"Found {total} images, converting...")
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    for img_path in image_files:
        out_path = output_dir / img_path.name
        print(f"Processing: {img_path.name}", end='')
        if convert_image(img_path, out_path):
            success += 1
            print(" ✓")
        else:
            print(" ✗")
    
    return success, total


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='Convert images to grayscale')
    parser.add_argument('input', type=Path, help='Input directory')
    parser.add_argument('output', type=Path, help='Output directory')
    parser.add_argument('-q', '--quality', type=int, default=95, help='JPEG quality (1-100)')
    args = parser.parse_args()
    
    # 验证输入目录
    if not args.input.exists():
        print(f"Error: Input directory not found: {args.input}")
        return 1
    
    if not args.input.is_dir():
        print(f"Error: Input path is not a directory: {args.input}")
        return 1
    
    # 执行转换
    success, total = batch_convert(args.input, args.output)
    
    # 输出结果
    print(f"\n{'='*40}")
    print(f"Total: {total}, Success: {success}, Failed: {total - success}")
    
    return 0 if success == total else 1


if __name__ == '__main__':
    sys.exit(main())

