"""
图片格式转换核心模块
"""
import os
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from PIL import Image

# 支持的图片格式
SUPPORTED_FORMATS = {
    'jpg': 'JPEG',
    'jpeg': 'JPEG',
    'png': 'PNG',
    'gif': 'GIF',
    'bmp': 'BMP',
    'webp': 'WebP',
    'ico': 'ICO',
    'tiff': 'TIFF',
}

# 支持读取的扩展名
READABLE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico', '.tiff', '.tif']

# 支持输出的格式
OUTPUT_FORMATS = ['jpg', 'png', 'gif', 'bmp', 'webp', 'ico']


def get_format_from_extension(ext: str) -> Optional[str]:
    """从扩展名获取PIL格式名称"""
    ext = ext.lower().lstrip('.')
    return SUPPORTED_FORMATS.get(ext)


def is_supported_file(filepath: str) -> bool:
    """检查文件是否为支持的图片格式"""
    ext = Path(filepath).suffix.lower()
    return ext in READABLE_EXTENSIONS


def convert_image(
    input_path: str,
    output_path: str,
    output_format: str,
    quality: int = 85,
    resize: Optional[Tuple[int, int]] = None,
    keep_aspect_ratio: bool = True,
    crop_rect: Optional[Tuple[int, int, int, int]] = None,
) -> Tuple[bool, str]:
    """
    转换单个图片
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        output_format: 输出格式 (jpg, png, gif, bmp, webp, ico)
        quality: 压缩质量 (1-100)，仅对有损格式有效
        resize: 调整尺寸 (width, height)，None表示不调整
        keep_aspect_ratio: 是否保持宽高比
        crop_rect: 裁剪区域 (left, top, right, bottom)，None表示不裁剪
    
    Returns:
        (success, message) 成功状态和消息
    """
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 处理调色板模式图片
        if img.mode == 'P':
            if output_format.lower() in ['jpg', 'jpeg', 'bmp']:
                img = img.convert('RGB')
            elif output_format.lower() == 'png':
                if 'transparency' in img.info:
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
        
        # 处理RGBA模式
        if img.mode == 'RGBA':
            if output_format.lower() in ['jpg', 'jpeg', 'bmp']:
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
        
        # 裁剪图片
        if crop_rect:
            left, top, right, bottom = crop_rect
            # 确保裁剪区域在图片范围内
            left = max(0, min(left, img.width))
            top = max(0, min(top, img.height))
            right = max(left, min(right, img.width))
            bottom = max(top, min(bottom, img.height))
            img = img.crop((left, top, right, bottom))
        
        # 调整尺寸
        if resize:
            width, height = resize
            if keep_aspect_ratio:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存参数
        save_kwargs = {}
        pil_format = get_format_from_extension(output_format)
        
        if pil_format == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif pil_format == 'PNG':
            save_kwargs['optimize'] = True
        elif pil_format == 'WebP':
            save_kwargs['quality'] = quality
        elif pil_format == 'GIF':
            pass  # GIF有特殊处理
        elif pil_format == 'ICO':
            # ICO需要特殊尺寸处理
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            save_kwargs['sizes'] = sizes
        
        # 保存图片
        img.save(output_path, format=pil_format, **save_kwargs)
        
        return True, f"转换成功: {os.path.basename(output_path)}"
        
    except Exception as e:
        return False, f"转换失败: {str(e)}"


def batch_convert(
    input_files: List[str],
    output_dir: str,
    output_format: str,
    quality: int = 85,
    resize: Optional[Tuple[int, int]] = None,
    keep_aspect_ratio: bool = True,
    crop_rects: Optional[dict] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Tuple[int, int, List[str]]:
    """
    批量转换图片
    
    Args:
        input_files: 输入文件列表
        output_dir: 输出目录
        output_format: 输出格式
        quality: 压缩质量
        resize: 调整尺寸
        keep_aspect_ratio: 是否保持宽高比
        crop_rects: 裁剪区域字典 {filepath: (left, top, right, bottom)}
        progress_callback: 进度回调函数 (current, total, message)
    
    Returns:
        (success_count, fail_count, error_messages)
    """
    success_count = 0
    fail_count = 0
    errors = []
    
    total = len(input_files)
    crop_rects = crop_rects or {}
    
    for i, input_path in enumerate(input_files):
        # 生成输出文件名
        base_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{base_name}.{output_format}")
        
        # 处理重名文件
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}.{output_format}")
            counter += 1
        
        # 获取该文件的裁剪区域
        crop_rect = crop_rects.get(input_path)
        
        # 转换
        success, message = convert_image(
            input_path, output_path, output_format,
            quality, resize, keep_aspect_ratio, crop_rect
        )
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            errors.append(f"{os.path.basename(input_path)}: {message}")
        
        # 回调进度
        if progress_callback:
            progress_callback(i + 1, total, message)
    
    return success_count, fail_count, errors
