"""
NCM 文件转换模块
用于解密网易云音乐加密格式(.ncm)并转换为 MP3/FLAC
"""
import os
from pathlib import Path
from typing import List, Tuple, Optional, Callable

try:
    from ncmdump import NeteaseCloudMusicFile
except ImportError:
    NeteaseCloudMusicFile = None


def is_ncm_file(filepath: str) -> bool:
    """检查文件是否为 NCM 格式"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(8)
            # NCM 文件魔数: CTENFDAM (网易云音乐加密格式)
            return len(header) >= 8 and header[:8] == b'CTENFDAM'
    except:
        return False


def get_ncm_info(filepath: str) -> Optional[dict]:
    """
    获取 NCM 文件信息
    
    Args:
        filepath: NCM 文件路径
    
    Returns:
        文件信息字典，包含 size 等
    """
    try:
        size = os.path.getsize(filepath)
        return {
            'size': size,
            'name': os.path.basename(filepath)
        }
    except:
        return None


def ncm_to_audio(
    input_path: str,
    output_path: str,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Tuple[bool, str]:
    """
    将 NCM 文件解密并转换为音频文件
    
    Args:
        input_path: NCM 文件路径
        output_path: 输出文件路径
        progress_callback: 进度回调函数
    
    Returns:
        (success, message)
    """
    if NeteaseCloudMusicFile is None:
        return False, "未安装 ncmdump 库，请运行: pip install ncmdump"
    
    try:
        if progress_callback:
            progress_callback("正在解密 NCM 文件...")
        
        # 解密 NCM 文件
        ncm = NeteaseCloudMusicFile(input_path)
        ncm.decrypt()
        
        # 获取音频格式
        # ncmdump 会自动检测输出格式，这里默认使用 mp3
        # 但如果需要保持原始格式，需要检查文件内容
        
        if progress_callback:
            progress_callback("正在导出音频文件...")
        
        # 导出音频
        ncm.dump_music(output_path)
        
        if progress_callback:
            progress_callback("转换完成!")
        
        return True, f"转换成功: {os.path.basename(output_path)}"
        
    except Exception as e:
        return False, f"转换失败: {str(e)}"


def batch_ncm_to_audio(
    input_files: List[str],
    output_dir: str,
    output_format: str = 'mp3',
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Tuple[int, int, List[str]]:
    """
    批量将 NCM 文件转换为音频文件
    
    Args:
        input_files: NCM 文件列表
        output_dir: 输出目录
        output_format: 输出格式 (mp3, flac 等)
        progress_callback: 进度回调函数 (current, total, message)
    
    Returns:
        (success_count, fail_count, error_messages)
    """
    success_count = 0
    fail_count = 0
    errors = []
    
    total = len(input_files)
    
    for i, input_path in enumerate(input_files):
        # 生成输出文件名
        base_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{base_name}.{output_format}")
        
        # 处理重名文件
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}.{output_format}")
            counter += 1
        
        def single_progress(msg: str):
            if progress_callback:
                progress_callback(i + 1, total, msg)
        
        # 转换
        success, message = ncm_to_audio(input_path, output_path, single_progress)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            errors.append(f"{os.path.basename(input_path)}: {message}")
    
    return success_count, fail_count, errors
