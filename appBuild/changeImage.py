#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片批量转灰度工具

将指定目录中的图片批量转换为灰度图，支持多种图片格式
"""
import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    print("错误：需要安装 Pillow 库，请执行 pip install Pillow")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # tqdm 为可选依赖

# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ImageConvertError(Exception):
    """图片转换异常"""


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
            # 避免覆盖同名文件
            if output_path.exists():
                stem = output_path.stem
                suffix = output_path.suffix
                counter = 1
                while output_path.exists():
                    output_path = output_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
            gray.save(output_path, quality=quality)
        return True
    except UnidentifiedImageError as e:
        raise ImageConvertError(f"无法识别的图片格式：{e}")
    except OSError as e:
        raise ImageConvertError(f"文件读写错误：{e}")
    except Exception as e:
        raise ImageConvertError(f"转换失败：{e}")


def batch_convert(input_dir: Path, output_dir: Path, quality: int = 95, 
                  max_workers: int = 4) -> tuple[int, int]:
    """批量转换目录中的图片
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :param quality: JPEG 质量
    :param max_workers: 最大并行线程数
    :return: (成功数，总数)
    """
    # 查找所有图片
    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]
    
    total = len(image_files)
    if total == 0:
        logger.warning("未找到图片文件")
        return 0, 0
    
    logger.info(f"找到 {total} 张图片，开始转换...")
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    failed = []
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_image, img_path, output_dir / img_path.name, quality): img_path
            for img_path in image_files
        }
        
        # 使用 tqdm 显示进度（如果可用）
        iterator = as_completed(futures)
        if tqdm:
            iterator = tqdm(iterator, total=total, desc="转换进度")
        
        for future in iterator:
            img_path = futures[future]
            try:
                future.result()
                success += 1
                if not tqdm:
                    logger.info(f"✓ {img_path.name}")
            except ImageConvertError as e:
                failed.append((img_path.name, str(e)))
                if not tqdm:
                    logger.error(f"✗ {img_path.name} ({e})")
    
    # 输出失败详情
    if failed:
        logger.warning(f"\n失败文件详情：")
        for name, error in failed:
            logger.warning(f"  {name}: {error}")
    
    return success, total


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='图片批量转灰度工具')
    parser.add_argument('input', type=Path, help='输入目录')
    parser.add_argument('output', type=Path, help='输出目录')
    parser.add_argument('-q', '--quality', type=int, default=95, 
                       help='JPEG 质量 (1-100)，默认 95')
    parser.add_argument('-w', '--workers', type=int, default=4,
                       help='并行线程数，默认 4')
    args = parser.parse_args()
    
    # 验证输入目录
    if not args.input.exists():
        logger.error(f"输入目录不存在：{args.input}")
        return 1
    
    if not args.input.is_dir():
        logger.error(f"输入路径不是目录：{args.input}")
        return 1
    
    if not 1 <= args.quality <= 100:
        logger.error(f"质量参数必须在 1-100 之间：{args.quality}")
        return 1
    
    # 执行转换
    success, total = batch_convert(args.input, args.output, args.quality, args.workers)
    
    # 输出结果
    logger.info(f"\n{'='*40}")
    logger.info(f"总计：{total} 张，成功：{success} 张，失败：{total - success} 张")
    
    return 0 if success == total else 1


if __name__ == '__main__':
    sys.exit(main())
