#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片批量转灰度工具

将指定目录中的图片批量转换为灰度图，支持多种图片格式
"""
import argparse
import sys
from pathlib import Path
from PIL import Image

# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}


class ImageConvertError(Exception):
    """图片转换异常"""
    pass


def convert_image(input_path: Path, output_path: Path, quality: int = 95) -> bool:
    """转换单张图片为灰度
    
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param quality: JPEG 质量 (1-100)
    :return: 是否成功
    :raises ImageConvertError: 转换失败时
    """
    try:
        with Image.open(input_path) as img:
            gray = img.convert('L')
            gray.save(output_path, quality=quality)
        return True
    except Exception as e:
        raise ImageConvertError(f"转换失败：{e}")


def batch_convert(input_dir: Path, output_dir: Path, quality: int = 95) -> tuple[int, int]:
    """批量转换目录中的图片
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :param quality: JPEG 质量
    :return: (成功数，总数)
    """
    # 查找所有图片
    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]
    
    total = len(image_files)
    if total == 0:
        print("未找到图片文件")
        return 0, 0
    
    print(f"找到 {total} 张图片，开始转换...")
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    for i, img_path in enumerate(image_files, 1):
        out_path = output_dir / img_path.name
        
        # 显示进度
        progress = f"[{i}/{total}] {img_path.name}"
        try:
            convert_image(img_path, out_path)
            success += 1
            print(f"{progress} ✓")
        except ImageConvertError as e:
            print(f"{progress} ✗ ({e})")
    
    return success, total


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='图片批量转灰度工具')
    parser.add_argument('input', type=Path, help='输入目录')
    parser.add_argument('output', type=Path, help='输出目录')
    parser.add_argument('-q', '--quality', type=int, default=95, 
                       help='JPEG 质量 (1-100)，默认 95')
    args = parser.parse_args()
    
    # 验证输入目录
    if not args.input.exists():
        print(f"错误：输入目录不存在：{args.input}")
        return 1
    
    if not args.input.is_dir():
        print(f"错误：输入路径不是目录：{args.input}")
        return 1
    
    # 执行转换
    success, total = batch_convert(args.input, args.output, args.quality)
    
    # 输出结果
    print(f"\n{'='*40}")
    print(f"总计：{total} 张，成功：{success} 张，失败：{total - success} 张")
    
    return 0 if success == total else 1


if __name__ == '__main__':
    sys.exit(main())
