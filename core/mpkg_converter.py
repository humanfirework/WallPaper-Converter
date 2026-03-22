"""
MPKG 文件转换模块
用于解析 Wallpaper Engine 的 .mpkg 文件并提取其中的 mp4 视频文件
"""
import os
import struct
from pathlib import Path
from typing import List, Tuple, Optional, Callable, Dict


class MPKGFile:
    """MPKG 文件条目"""
    def __init__(self, name: str, offset: int, size: int):
        self.name = name
        self.offset = offset
        self.size = size
    
    def __repr__(self):
        return f"MPKGFile(name='{self.name}', offset={self.offset}, size={self.size})"


class MPKGParser:
    """MPKG 文件解析器"""
    
    MAGIC = b'PKGM'
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.version: str = ""
        self.files: List[MPKGFile] = []
        self._header_size = 0
        self._data_start = 0
    
    def parse(self) -> bool:
        """
        解析 MPKG 文件结构
        
        Returns:
            是否解析成功
        """
        try:
            with open(self.filepath, 'rb') as f:
                # 读取头部 (16 字节)
                header = f.read(16)
                if len(header) < 16:
                    return False
                
                # 解析头部
                # 前 4 字节未知，跳过
                magic = header[4:8]
                if magic != self.MAGIC:
                    raise ValueError(f"无效的 MPKG 文件: 魔数不匹配 (期望 {self.MAGIC}, 实际 {magic})")
                
                self.version = header[8:12].decode('ascii', errors='ignore')
                file_count = struct.unpack('<I', header[12:16])[0]
                
                # 解析文件表
                self.files = []
                for _ in range(file_count):
                    # 读取文件名长度
                    name_len_bytes = f.read(4)
                    if len(name_len_bytes) < 4:
                        break
                    name_len = struct.unpack('<I', name_len_bytes)[0]
                    
                    # 读取文件名
                    name = f.read(name_len).decode('utf-8', errors='ignore')
                    
                    # 读取偏移和大小
                    offset_size = f.read(8)
                    if len(offset_size) < 8:
                        break
                    file_offset = struct.unpack('<I', offset_size[0:4])[0]
                    file_size = struct.unpack('<I', offset_size[4:8])[0]
                    
                    self.files.append(MPKGFile(name, file_offset, file_size))
                
                # 计算数据区起始位置
                self._data_start = f.tell()
                
            return True
            
        except Exception as e:
            raise ValueError(f"解析 MPKG 文件失败: {str(e)}")
    
    def get_file_info(self, filename: str) -> Optional[MPKGFile]:
        """获取指定文件的信息"""
        for f in self.files:
            if f.name == filename:
                return f
        return None
    
    def extract_file(self, filename: str, output_path: str) -> Tuple[bool, str]:
        """
        提取指定文件
        
        Args:
            filename: 要提取的文件名
            output_path: 输出路径
        
        Returns:
            (success, message)
        """
        file_info = self.get_file_info(filename)
        if not file_info:
            return False, f"文件 '{filename}' 不存在于 MPKG 包中"
        
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(self.filepath, 'rb') as f:
                # 定位到文件数据位置
                f.seek(self._data_start + file_info.offset)
                
                # 读取并写入文件
                data = f.read(file_info.size)
                with open(output_path, 'wb') as out:
                    out.write(data)
            
            return True, f"提取成功: {os.path.basename(output_path)}"
            
        except Exception as e:
            return False, f"提取失败: {str(e)}"
    
    def extract_all(self, output_dir: str) -> Tuple[int, int, List[str]]:
        """
        提取所有文件
        
        Args:
            output_dir: 输出目录
        
        Returns:
            (success_count, fail_count, error_messages)
        """
        success_count = 0
        fail_count = 0
        errors = []
        
        for file_info in self.files:
            output_path = os.path.join(output_dir, file_info.name)
            success, message = self.extract_file(file_info.name, output_path)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(message)
        
        return success_count, fail_count, errors


def mpkg_to_mp4(
    input_path: str,
    output_path: str,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Tuple[bool, str]:
    """
    将 MPKG 文件中的 MP4 视频提取出来
    
    Args:
        input_path: MPKG 文件路径
        output_path: 输出 MP4 文件路径
        progress_callback: 进度回调函数
    
    Returns:
        (success, message)
    """
    try:
        if progress_callback:
            progress_callback("正在解析 MPKG 文件...")
        
        # 解析 MPKG 文件
        parser = MPKGParser(input_path)
        parser.parse()
        
        # 检查是否存在 wallpaper.mp4
        mp4_info = parser.get_file_info('wallpaper.mp4')
        if not mp4_info:
            return False, "MPKG 文件中未找到 wallpaper.mp4"
        
        if progress_callback:
            progress_callback(f"找到视频文件，大小: {mp4_info.size / 1024 / 1024:.2f} MB")
            progress_callback("正在提取视频...")
        
        # 提取文件
        success, message = parser.extract_file('wallpaper.mp4', output_path)
        
        if success and progress_callback:
            progress_callback("提取完成!")
        
        return success, message
        
    except Exception as e:
        return False, f"转换失败: {str(e)}"


def batch_mpkg_to_mp4(
    input_files: List[str],
    output_dir: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Tuple[int, int, List[str]]:
    """
    批量将 MPKG 文件转换为 MP4
    
    Args:
        input_files: MPKG 文件列表
        output_dir: 输出目录
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
        output_path = os.path.join(output_dir, f"{base_name}.mp4")
        
        # 处理重名文件
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}.mp4")
            counter += 1
        
        def single_progress(msg: str):
            if progress_callback:
                progress_callback(i + 1, total, msg)
        
        # 转换
        success, message = mpkg_to_mp4(input_path, output_path, single_progress)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            errors.append(f"{os.path.basename(input_path)}: {message}")
    
    return success_count, fail_count, errors


def is_mpkg_file(filepath: str) -> bool:
    """检查文件是否为 MPKG 格式"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(8)
            return len(header) >= 8 and header[4:8] == MPKGParser.MAGIC
    except:
        return False
