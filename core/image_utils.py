"""
图片处理工具函数
"""
import os
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image


def get_image_info(filepath: str) -> Optional[dict]:
    """
    获取图片信息
    
    Returns:
        {
            'width': 宽度,
            'height': 高度,
            'format': 格式,
            'mode': 颜色模式,
            'size': 文件大小(字节)
        }
    """
    try:
        with Image.open(filepath) as img:
            file_size = os.path.getsize(filepath)
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size': file_size,
            }
    except Exception:
        return None


def calculate_new_size(
    original_width: int,
    original_height: int,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    keep_aspect_ratio: bool = True,
) -> Tuple[int, int]:
    """
    计算新尺寸
    
    Args:
        original_width: 原始宽度
        original_height: 原始高度
        max_width: 最大宽度
        max_height: 最大高度
        keep_aspect_ratio: 是否保持宽高比
    
    Returns:
        (new_width, new_height)
    """
    if max_width is None and max_height is None:
        return original_width, original_height
    
    if not keep_aspect_ratio:
        return max_width or original_width, max_height or original_height
    
    # 计算缩放比例
    ratio = 1.0
    
    if max_width and max_height:
        ratio = min(max_width / original_width, max_height / original_height)
    elif max_width:
        ratio = max_width / original_width
    elif max_height:
        ratio = max_height / original_height
    
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return new_width, new_height


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def get_unique_filename(directory: str, base_name: str, extension: str) -> str:
    """
    获取唯一的文件名
    
    Args:
        directory: 目录路径
        base_name: 基础文件名(不含扩展名)
        extension: 扩展名(不含点)
    
    Returns:
        完整的文件路径
    """
    filepath = os.path.join(directory, f"{base_name}.{extension}")
    
    if not os.path.exists(filepath):
        return filepath
    
    counter = 1
    while True:
        filepath = os.path.join(directory, f"{base_name}_{counter}.{extension}")
        if not os.path.exists(filepath):
            return filepath
        counter += 1


def estimate_output_size(
    input_path: str,
    output_format: str,
    quality: int = 85,
) -> Optional[int]:
    """
    估算输出文件大小
    
    Note: 这是一个粗略估算，实际大小可能有差异
    """
    info = get_image_info(input_path)
    if not info:
        return None
    
    # 像素数量
    pixels = info['width'] * info['height']
    
    # 根据格式估算压缩率
    compression_ratios = {
        'jpg': 0.1 * (quality / 100) + 0.05,
        'jpeg': 0.1 * (quality / 100) + 0.05,
        'png': 0.3,
        'webp': 0.08 * (quality / 100) + 0.04,
        'gif': 0.5,
        'bmp': 3.0,  # BMP基本不压缩
        'ico': 0.3,
    }
    
    ratio = compression_ratios.get(output_format.lower(), 0.3)
    # 每像素约3字节(RGB)
    estimated_bytes = int(pixels * 3 * ratio)
    
    return estimated_bytes
