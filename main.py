"""
图片格式转换工具
支持批量转换、尺寸调整、质量压缩
"""
import sys
from pathlib import Path

# 确保模块路径正确
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import main

if __name__ == "__main__":
    main()
