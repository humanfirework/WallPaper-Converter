"""
图片格式转换工具 - 主界面 (现代化设计)
支持图片格式转换和 MPKG 转 MP4
"""
import os
import sys
import ctypes
from pathlib import Path
from typing import List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QComboBox,
    QSlider, QSpinBox, QCheckBox, QGroupBox, QFileDialog,
    QProgressBar, QMessageBox, QFrame, QAbstractItemView,
    QGraphicsDropShadowEffect, QScrollArea, QSizePolicy,
    QStackedWidget, QRadioButton, QButtonGroup, QGraphicsOpacityEffect,
    QSplashScreen,
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, 
    QEasingCurve, QParallelAnimationGroup, QRect, QPoint, pyqtProperty,
    QTimer
)
from PyQt5.QtGui import (
    QFont, QColor, QDragEnterEvent, QDropEvent, QPalette, 
    QLinearGradient, QPainter, QBrush, QPen, QRadialGradient, QPixmap,
    QPainterPath, QTransform
)

# 添加父目录到路径 (确保 core 模块可导入)
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.converter import (
    batch_convert, is_supported_file, OUTPUT_FORMATS, READABLE_EXTENSIONS
)
from core.image_utils import format_file_size, get_image_info
from core.mpkg_converter import (
    batch_mpkg_to_mp4, is_mpkg_file
)
from ui.preview_dialog import PreviewDialog

# Windows API 相关常量用于亚克力效果
class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int),
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_int),
    ]

def set_acrylic_effect(hwnd, color=0x00F2F2F2):
    """启用 Windows 亚克力效果"""
    accent = ACCENT_POLICY()
    accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
    accent.GradientColor = color
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19  # WCA_ACCENT_POLICY
    data.SizeOfData = ctypes.sizeof(accent)
    data.Data = ctypes.pointer(accent)
    
    ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))

# ==================== 现代简约设计系统 ====================
# 设计系统 - 颜色、字体、间距规范
DESIGN_SYSTEM = {
    "colors": {
        "primary": "#007aff",
        "primary_hover": "#0066cc",
        "primary_pressed": "#0055aa",
        "success": "#34c759",
        "warning": "#ff9500",
        "danger": "#ff3b30",
        "text_primary": "#1d1d1f",
        "text_secondary": "#6e6e73",
        "text_tertiary": "#86868b",
        "background": "#f5f5f7",
        "surface": "#ffffff",
        "border": "#e5e5ea",
        "border_hover": "#d1d1d6",
        "overlay": "rgba(0, 0, 0, 0.04)",
        "overlay_hover": "rgba(0, 0, 0, 0.08)",
    },
    "spacing": {
        "xs": "4px",
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "20px",
        "2xl": "24px",
        "3xl": "32px",
    },
    "radius": {
        "sm": "6px",
        "md": "8px",
        "lg": "12px",
        "xl": "16px",
    },
    "font": {
        "xs": "11px",
        "sm": "12px",
        "md": "13px",
        "lg": "14px",
        "xl": "15px",
        "2xl": "17px",
    }
}

MODERN_STYLE = f"""
/* 全局样式 */
QMainWindow {{
    background: transparent;
}}

QWidget#mainContainer {{
    background-color: {DESIGN_SYSTEM['colors']['background']};
    border-radius: {DESIGN_SYSTEM['radius']['xl']};
}}

/* 自定义标题栏 */
QWidget#titleBar {{
    background: transparent;
    min-height: 52px;
}}

QLabel#windowTitle {{
    font-weight: 600;
    font-size: {DESIGN_SYSTEM['font']['xl']};
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    padding-left: {DESIGN_SYSTEM['spacing']['xl']};
}}

QPushButton#sysBtn {{
    background: transparent;
    border: none;
    border-radius: {DESIGN_SYSTEM['radius']['sm']};
    padding: {DESIGN_SYSTEM['spacing']['sm']} {DESIGN_SYSTEM['spacing']['lg']};
    font-size: 18px;
    color: {DESIGN_SYSTEM['colors']['text_tertiary']};
    font-weight: 500;
}}

QPushButton#sysBtn:hover {{
    background-color: {DESIGN_SYSTEM['colors']['overlay']};
    color: {DESIGN_SYSTEM['colors']['text_primary']};
}}

QPushButton#closeBtn:hover {{
    background-color: {DESIGN_SYSTEM['colors']['danger']};
    color: white;
}}

/* 分组框 - 简约卡片风格 */
QGroupBox {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: none;
    border-radius: {DESIGN_SYSTEM['radius']['lg']};
    margin-top: {DESIGN_SYSTEM['spacing']['sm']};
    padding: {DESIGN_SYSTEM['spacing']['lg']} {DESIGN_SYSTEM['spacing']['lg']} {DESIGN_SYSTEM['spacing']['lg']} {DESIGN_SYSTEM['spacing']['lg']};
    font-weight: 600;
    font-size: {DESIGN_SYSTEM['font']['md']};
    color: {DESIGN_SYSTEM['colors']['primary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: {DESIGN_SYSTEM['spacing']['lg']};
    padding: 0 {DESIGN_SYSTEM['spacing']['sm']};
    background-color: transparent;
    color: {DESIGN_SYSTEM['colors']['primary']};
}}

/* 按钮 - 扁平简约风格 */
QPushButton {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
    border-radius: {DESIGN_SYSTEM['radius']['md']};
    padding: {DESIGN_SYSTEM['spacing']['md']} {DESIGN_SYSTEM['spacing']['xl']};
    font-weight: 500;
    font-size: {DESIGN_SYSTEM['font']['md']};
    color: {DESIGN_SYSTEM['colors']['text_primary']};
}}

QPushButton:hover {{
    background-color: {DESIGN_SYSTEM['colors']['overlay']};
    border-color: {DESIGN_SYSTEM['colors']['border_hover']};
}}

QPushButton:pressed {{
    background-color: {DESIGN_SYSTEM['colors']['overlay_hover']};
}}

QPushButton:disabled {{
    background-color: {DESIGN_SYSTEM['colors']['background']};
    border-color: {DESIGN_SYSTEM['colors']['border']};
    color: {DESIGN_SYSTEM['colors']['text_tertiary']};
}}

/* 下拉框 */
QComboBox {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
    border-radius: {DESIGN_SYSTEM['radius']['md']};
    padding: {DESIGN_SYSTEM['spacing']['md']} {DESIGN_SYSTEM['spacing']['lg']};
    min-width: 120px;
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    font-size: {DESIGN_SYSTEM['font']['md']};
}}

QComboBox:hover {{
    background-color: {DESIGN_SYSTEM['colors']['overlay']};
    border-color: {DESIGN_SYSTEM['colors']['border_hover']};
}}

QComboBox:focus {{
    border-color: {DESIGN_SYSTEM['colors']['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
    background: transparent;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {DESIGN_SYSTEM['colors']['text_tertiary']};
    margin-right: {DESIGN_SYSTEM['spacing']['sm']};
}}

QComboBox QAbstractItemView {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
    border-radius: {DESIGN_SYSTEM['radius']['lg']};
    selection-background-color: {DESIGN_SYSTEM['colors']['primary']};
    selection-color: white;
    padding: {DESIGN_SYSTEM['spacing']['sm']};
    outline: none;
}}

/* 输入框 */
QSpinBox {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
    border-radius: {DESIGN_SYSTEM['radius']['md']};
    padding: {DESIGN_SYSTEM['spacing']['md']} {DESIGN_SYSTEM['spacing']['md']};
    min-width: 80px;
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    font-size: {DESIGN_SYSTEM['font']['md']};
}}

QSpinBox:hover {{
    background-color: {DESIGN_SYSTEM['colors']['overlay']};
    border-color: {DESIGN_SYSTEM['colors']['border_hover']};
}}

QSpinBox:focus {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border-color: {DESIGN_SYSTEM['colors']['primary']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: transparent;
    border: none;
    width: 24px;
}}

QSpinBox::up-arrow, QSpinBox::down-arrow {{
    width: 8px;
    height: 8px;
}}

/* 列表 - 简约风格 */
QListWidget {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
    border-radius: {DESIGN_SYSTEM['radius']['lg']};
    padding: {DESIGN_SYSTEM['spacing']['sm']};
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    border-radius: {DESIGN_SYSTEM['radius']['md']};
    padding: {DESIGN_SYSTEM['spacing']['md']} {DESIGN_SYSTEM['spacing']['lg']};
    margin: 2px 0;
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    font-size: {DESIGN_SYSTEM['font']['md']};
}}

QListWidget::item:hover {{
    background-color: {DESIGN_SYSTEM['colors']['overlay']};
}}

QListWidget::item:selected {{
    background-color: {DESIGN_SYSTEM['colors']['primary']};
    color: white;
}}

/* 进度条 - 简约风格 */
QProgressBar {{
    background-color: {DESIGN_SYSTEM['colors']['border']};
    border: none;
    border-radius: {DESIGN_SYSTEM['radius']['sm']};
    height: 8px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background: {DESIGN_SYSTEM['colors']['primary']};
    border-radius: {DESIGN_SYSTEM['radius']['sm']};
}}

/* 滑块 - 简约风格 */
QSlider::groove:horizontal {{
    background: {DESIGN_SYSTEM['colors']['border']};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: white;
    border: 3px solid {DESIGN_SYSTEM['colors']['primary']};
    width: 24px;
    height: 24px;
    margin: -9px 0;
    border-radius: 12px;
}}

QSlider::handle:horizontal:hover {{
    background: {DESIGN_SYSTEM['colors']['surface']};
    border-color: {DESIGN_SYSTEM['colors']['primary_hover']};
}}

QSlider::sub-page:horizontal {{
    background: {DESIGN_SYSTEM['colors']['primary']};
    border-radius: 3px;
}}

QSlider::add-page:horizontal {{
    background: {DESIGN_SYSTEM['colors']['border']};
    border-radius: 3px;
}}

/* 标签 */
QLabel {{
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: {DESIGN_SYSTEM['font']['2xl']};
    font-weight: 600;
    color: {DESIGN_SYSTEM['colors']['text_primary']};
}}

QLabel#subtitleLabel {{
    font-size: {DESIGN_SYSTEM['font']['sm']};
    color: {DESIGN_SYSTEM['colors']['text_secondary']};
    font-weight: 400;
}}

QLabel#countLabel {{
    font-size: {DESIGN_SYSTEM['font']['md']};
    font-weight: 600;
    color: {DESIGN_SYSTEM['colors']['primary']};
}}

QLabel#sectionTitle {{
    font-size: {DESIGN_SYSTEM['font']['md']};
    font-weight: 600;
    color: {DESIGN_SYSTEM['colors']['primary']};
    padding: {DESIGN_SYSTEM['spacing']['sm']} 0 {DESIGN_SYSTEM['spacing']['xs']} 0;
}}

/* 滚动条 - 极简风格 */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: rgba(0, 0, 0, 0.15);
    border-radius: 3px;
    min-height: 32px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(0, 0, 0, 0.25);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

/* 面板 - 卡片风格 */
QFrame#panel, QFrame#leftPanel, QFrame#rightPanel {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: none;
    border-radius: {DESIGN_SYSTEM['radius']['xl']};
}}

QFrame#settingsCard {{
    background-color: {DESIGN_SYSTEM['colors']['surface']};
    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
    border-radius: {DESIGN_SYSTEM['radius']['lg']};
}}

QFrame#settingsCard:hover {{
    border: 1px solid {DESIGN_SYSTEM['colors']['border_hover']};
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea QScrollBar {{
    background: transparent;
}}

QScrollArea QScrollBar:vertical {{
    background: transparent;
    width: 6px;
}}

QScrollArea QScrollBar::handle:vertical {{
    background: rgba(0, 0, 0, 0.15);
    border-radius: 3px;
    min-height: 32px;
}}

/* 单选按钮 - 简约风格 */
QRadioButton {{
    spacing: {DESIGN_SYSTEM['spacing']['md']};
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    font-size: {DESIGN_SYSTEM['font']['lg']};
    font-weight: 500;
    padding: {DESIGN_SYSTEM['spacing']['sm']} {DESIGN_SYSTEM['spacing']['lg']};
    background: {DESIGN_SYSTEM['colors']['surface']};
    border-radius: {DESIGN_SYSTEM['radius']['md']};
}}

QRadioButton:hover {{
    background: {DESIGN_SYSTEM['colors']['overlay']};
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid {DESIGN_SYSTEM['colors']['border']};
    background: {DESIGN_SYSTEM['colors']['surface']};
}}

QRadioButton::indicator:hover {{
    border-color: {DESIGN_SYSTEM['colors']['primary']};
}}

QRadioButton::indicator:checked {{
    border-color: {DESIGN_SYSTEM['colors']['primary']};
    background: {DESIGN_SYSTEM['colors']['primary']};
}}

/* 复选框 - 简约风格 */
QCheckBox {{
    spacing: {DESIGN_SYSTEM['spacing']['md']};
    color: {DESIGN_SYSTEM['colors']['text_primary']};
    font-size: {DESIGN_SYSTEM['font']['md']};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: {DESIGN_SYSTEM['radius']['sm']};
    border: 2px solid {DESIGN_SYSTEM['colors']['border']};
    background: {DESIGN_SYSTEM['colors']['surface']};
}}

QCheckBox::indicator:hover {{
    border-color: {DESIGN_SYSTEM['colors']['primary']};
}}

QCheckBox::indicator:checked {{
    border-color: {DESIGN_SYSTEM['colors']['primary']};
    background: {DESIGN_SYSTEM['colors']['primary']};
}}

QCheckBox:disabled {{
    color: {DESIGN_SYSTEM['colors']['text_tertiary']};
}}

QCheckBox::indicator:disabled {{
    border-color: {DESIGN_SYSTEM['colors']['border']};
    background: {DESIGN_SYSTEM['colors']['background']};
}}
"""

class ModernButton(QPushButton):
    """现代化按钮（简约风格，带阴影动画）"""
    def __init__(self, text="", parent=None, is_primary=False):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setCursor(Qt.PointingHandCursor)
        
        # 阴影效果 - 优化性能
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(self.shadow)
        self.shadow.setEnabled(False)
        
        if is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {DESIGN_SYSTEM['colors']['primary']};
                    border: none;
                    border-radius: {DESIGN_SYSTEM['radius']['md']};
                    color: white;
                    font-size: {DESIGN_SYSTEM['font']['lg']};
                    font-weight: 600;
                    padding: {DESIGN_SYSTEM['spacing']['md']} {DESIGN_SYSTEM['spacing']['2xl']};
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: {DESIGN_SYSTEM['colors']['primary_hover']};
                }}
                QPushButton:pressed {{
                    background: {DESIGN_SYSTEM['colors']['primary_pressed']};
                    padding-top: {DESIGN_SYSTEM['spacing']['lg']};
                    padding-bottom: {DESIGN_SYSTEM['spacing']['sm']};
                }}
                QPushButton:disabled {{
                    background: {DESIGN_SYSTEM['colors']['text_tertiary']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {DESIGN_SYSTEM['colors']['surface']};
                    border: 1px solid {DESIGN_SYSTEM['colors']['border']};
                    border-radius: {DESIGN_SYSTEM['radius']['md']};
                    color: {DESIGN_SYSTEM['colors']['text_primary']};
                    font-size: {DESIGN_SYSTEM['font']['md']};
                    font-weight: 500;
                    padding: {DESIGN_SYSTEM['spacing']['md']} {DESIGN_SYSTEM['spacing']['xl']};
                }}
                QPushButton:hover {{
                    background: {DESIGN_SYSTEM['colors']['overlay']};
                    border-color: {DESIGN_SYSTEM['colors']['border_hover']};
                }}
                QPushButton:pressed {{
                    background: {DESIGN_SYSTEM['colors']['overlay_hover']};
                    padding-top: {DESIGN_SYSTEM['spacing']['lg']};
                    padding-bottom: {DESIGN_SYSTEM['spacing']['sm']};
                }}
            """)

    def enterEvent(self, event):
        self.shadow.setEnabled(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shadow.setEnabled(False)
        super().leaveEvent(event)

class SettingsCard(QFrame):
    """设置卡片容器（增强层次感）"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsCard")
        
        self.setStyleSheet(f"""
            QFrame#settingsCard {{
                background-color: {DESIGN_SYSTEM['colors']['surface']};
                border: 1px solid {DESIGN_SYSTEM['colors']['border']};
                border-radius: {DESIGN_SYSTEM['radius']['lg']};
            }}
            QFrame#settingsCard:hover {{
                border: 1px solid {DESIGN_SYSTEM['colors']['border_hover']};
            }}
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            font-size: {DESIGN_SYSTEM['font']['lg']};
            font-weight: 600;
            color: {DESIGN_SYSTEM['colors']['text_primary']};
            padding: 0;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.main_layout.addLayout(header_layout)

    def addWidget(self, widget):
        self.main_layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.main_layout.addLayout(layout)

class ConvertWorker(QThread):
    """图片转换工作线程"""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(int, int, list)

    def __init__(self, files, output_dir, output_format, quality, resize, keep_ratio, crop_rects=None):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.output_format = output_format
        self.quality = quality
        self.resize = resize
        self.keep_ratio = keep_ratio
        self.crop_rects = crop_rects or {}

    def run(self):
        success, fail, errors = batch_convert(
            self.files,
            self.output_dir,
            self.output_format,
            self.quality,
            self.resize,
            self.keep_ratio,
            self.crop_rects,
            lambda c, t, m: self.progress.emit(c, t, m)
        )
        self.finished.emit(success, fail, errors)


class MPKGConvertWorker(QThread):
    """MPKG 转换工作线程"""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(int, int, list)

    def __init__(self, files, output_dir):
        super().__init__()
        self.files = files
        self.output_dir = output_dir

    def run(self):
        success, fail, errors = batch_mpkg_to_mp4(
            self.files,
            self.output_dir,
            lambda c, t, m: self.progress.emit(c, t, m)
        )
        self.finished.emit(success, fail, errors)


class FileListWidget(QListWidget):
    """支持拖拽的文件列表"""
    
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None, mode='image'):
        super().__init__(parent)
        self.setObjectName("dropArea")
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSpacing(2)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._mode = mode  # 'image' or 'mpkg'
        self._original_style = ""
        
    def set_mode(self, mode: str):
        """设置模式"""
        self._mode = mode
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
            event.acceptProposedAction()
            self._original_style = self.styleSheet()
            self.setStyleSheet("""
                QListWidget#dropArea {
                    border: 2px dashed #007aff;
                    background-color: #e8f4fd;
                }
            """)
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self._original_style)
        
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(self._original_style)
        files = []
        urls = event.mimeData().urls()
        print(f"[DEBUG] Drop event triggered, mode: {self._mode}, urls count: {len(urls)}")
        
        for url in urls:
            path = url.toLocalFile()
            print(f"[DEBUG] Processing path: {path}")
            print(f"[DEBUG] Is file: {os.path.isfile(path)}, Is dir: {os.path.isdir(path)}")
            
            if self._mode == 'mpkg':
                # MPKG 模式
                if os.path.isfile(path):
                    is_mpkg = is_mpkg_file(path)
                    print(f"[DEBUG] is_mpkg_file result: {is_mpkg}")
                    if is_mpkg:
                        files.append(path)
                elif os.path.isdir(path):
                    for root, _, filenames in os.walk(path):
                        for filename in filenames:
                            filepath = os.path.join(root, filename)
                            if is_mpkg_file(filepath):
                                files.append(filepath)
            else:
                # 图片模式
                if os.path.isfile(path) and is_supported_file(path):
                    files.append(path)
                elif os.path.isdir(path):
                    for root, _, filenames in os.walk(path):
                        for filename in filenames:
                            filepath = os.path.join(root, filename)
                            if is_supported_file(filepath):
                                files.append(filepath)
        
        print(f"[DEBUG] Files to add: {files}")
        if files:
            self.files_dropped.emit(files)
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_selected()
        else:
            super().keyPressEvent(event)

    def remove_selected(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))


class AnimatedStackedWidget(QStackedWidget):
    """带流畅切换动画的堆栈窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation = None
        self._opacity_effects = {}  # 存储每个widget的透明度效果
        
    def _get_opacity_effect(self, widget):
        """获取或创建widget的透明度效果"""
        if widget not in self._opacity_effects:
            effect = QGraphicsOpacityEffect(widget)
            effect.setOpacity(1.0)
            widget.setGraphicsEffect(effect)
            self._opacity_effects[widget] = effect
        return self._opacity_effects[widget]
        
    def setCurrentIndex(self, index):
        """带淡入淡出动画的切换"""
        # 如果是同一个索引或没有内容，直接设置
        if index == self.currentIndex():
            return
        
        target_widget = self.widget(index)
        if target_widget is None:
            return
        
        current_widget = self.currentWidget()
        
        # 如果没���当前widget（初始化状态），直接切换
        if current_widget is None:
            super().setCurrentIndex(index)
            return
        
        # 简化：直接切换，不做动画（动画可能导致显示问题）
        super().setCurrentIndex(index)

class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("格式转换工具")
        self.setMinimumSize(1000, 650)
        self.resize(1100, 750)
        
        # 设置无边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 性能优化：启用OpenGL加速（如果可用）
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        
        # 允许鼠标追踪以实现边缘缩放
        self.setMouseTracking(True)
        
        self.image_files: List[str] = []
        self.mpkg_files: List[str] = []
        self.worker = None
        self.crop_rects: dict = {}
        
        # 拖拽和缩放相关
        self._drag_pos = None
        self._resize_edge = None
        self._margin = 8 # 缩放感应边距（减小以提高精确度）
        
        # 动画相关
        self._fade_animation = None
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(16)  # ~60fps
        
        self.init_ui()
        self.connect_signals()
        self.apply_shadow_effects()
        
        # 延迟应用亚克力效果，确保窗口句柄已创建
        QTimer.singleShot(10, self._apply_acrylic)
        
        # 启动时的淡入动画
        self._setup_fade_in()

    def _apply_acrylic(self):
        # 简约风格不需要亚克力效果
        pass
    
    def _setup_fade_in(self):
        """设置窗口淡入动画"""
        self.setWindowOpacity(0.0)
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(300)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        QTimer.singleShot(50, self._fade_animation.start)

    def init_ui(self):
        """初始化界面"""
        # 主容器
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        self.main_container.setMouseTracking(True)
        self.setCentralWidget(self.main_container)
        
        self.root_layout = QVBoxLayout(self.main_container)
        self.root_layout.setContentsMargins(1, 1, 1, 1)
        self.root_layout.setSpacing(0)
        
        # 1. 自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setMouseTracking(True)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # 标题文字
        self.window_title_label = QLabel("格式转换工具")
        self.window_title_label.setObjectName("windowTitle")
        title_layout.addWidget(self.window_title_label)
        title_layout.addStretch()
        
        # 最小化按钮
        self.min_btn = QPushButton("−")
        self.min_btn.setObjectName("sysBtn")
        self.min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_btn)
        
        # 关闭按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("sysBtn")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        self.root_layout.addWidget(self.title_bar)
        
        # 2. 内容区域
        content_widget = QWidget()
        content_widget.setMouseTracking(True)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 8, 16, 16)
        content_layout.setSpacing(16)
        
        # 左侧：文件列表区域
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 50)
        
        # 右侧：设置区域
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 50)
        
        self.root_layout.addWidget(content_widget)

    def _get_resize_edge(self, pos):
        """判断鼠标是否在边缘"""
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        
        edge = 0
        if x < self._margin: edge |= int(Qt.LeftEdge)
        if x > w - self._margin: edge |= int(Qt.RightEdge)
        if y < self._margin: edge |= int(Qt.TopEdge)
        if y > h - self._margin: edge |= int(Qt.BottomEdge)
        return edge

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = self._get_resize_edge(event.pos())
            if edge:
                # 开启边缘缩放
                self.windowHandle().startSystemResize(Qt.Edges(edge))
            elif self.title_bar.underMouse():
                # 开启移动
                self.windowHandle().startSystemMove()
            event.accept()

    def mouseMoveEvent(self, event):
        # 改变光标形状提示缩放（优化性能）
        if not self._resize_timer.isActive():
            edge = self._get_resize_edge(event.pos())
            self._update_cursor_for_edge(edge)
        super().mouseMoveEvent(event)
    
    def _update_cursor_for_edge(self, edge):
        """根据边缘更新光标"""
        left_top = int(Qt.LeftEdge) | int(Qt.TopEdge)
        right_bottom = int(Qt.RightEdge) | int(Qt.BottomEdge)
        right_top = int(Qt.RightEdge) | int(Qt.TopEdge)
        left_bottom = int(Qt.LeftEdge) | int(Qt.BottomEdge)
        hor_edges = int(Qt.LeftEdge) | int(Qt.RightEdge)
        ver_edges = int(Qt.TopEdge) | int(Qt.BottomEdge)

        if edge == left_top or edge == right_bottom:
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge == right_top or edge == left_bottom:
            self.setCursor(Qt.SizeBDiagCursor)
        elif edge & hor_edges:
            self.setCursor(Qt.SizeHorCursor)
        elif edge & ver_edges:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def create_left_panel(self) -> QWidget:
        """创建左侧文件列表面板"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 模式切换 - 使用标签页风格
        mode_container = QWidget()
        mode_container.setStyleSheet("background: #f5f5f7; border-radius: 10px;")
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(4, 4, 4, 4)
        mode_layout.setSpacing(4)
        
        self.mode_group = QButtonGroup(self)
        
        self.image_mode_btn = QRadioButton("图片转换")
        self.image_mode_btn.setChecked(True)
        self.image_mode_btn.setStyleSheet("""
            QRadioButton {
                background: white;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: 600;
                color: #007aff;
            }
            QRadioButton:!checked {
                background: transparent;
                color: #86868b;
            }
            QRadioButton::indicator { width: 0; height: 0; }
        """)
        self.mode_group.addButton(self.image_mode_btn, 0)
        mode_layout.addWidget(self.image_mode_btn)
        
        self.mpkg_mode_btn = QRadioButton("MPKG 转 MP4")
        self.mpkg_mode_btn.setStyleSheet("""
            QRadioButton {
                background: white;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: 600;
                color: #007aff;
            }
            QRadioButton:!checked {
                background: transparent;
                color: #86868b;
            }
            QRadioButton::indicator { width: 0; height: 0; }
        """)
        self.mode_group.addButton(self.mpkg_mode_btn, 1)
        mode_layout.addWidget(self.mpkg_mode_btn)
        
        layout.addWidget(mode_container)
        
        # 标题区域
        self.title_label = QLabel("待转换图片")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("拖拽图片文件或文件夹到下方区域，或点击按钮添加")
        self.subtitle_label.setObjectName("subtitleLabel")
        layout.addWidget(self.subtitle_label)
        
        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12) # 增加间距
        
        self.add_btn = ModernButton("添加文件")
        self.add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_btn)
        
        self.add_folder_btn = ModernButton("添加文件夹")
        self.add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(self.add_folder_btn)
        
        btn_layout.addStretch()
        
        clear_btn = ModernButton("清空")
        clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 文件列表
        self.file_list = FileListWidget(mode='image')
        self.file_list.files_dropped.connect(self.add_files_to_list)
        self.file_list.itemDoubleClicked.connect(self.preview_file)
        self.file_list.setMinimumHeight(300)
        layout.addWidget(self.file_list, 1)
        
        # 底部状态
        bottom_layout = QHBoxLayout()
        
        self.file_count_label = QLabel("共 0 个文件")
        self.file_count_label.setObjectName("countLabel")
        bottom_layout.addWidget(self.file_count_label)
        
        bottom_layout.addStretch()
        
        self.preview_btn = ModernButton("预览/裁剪")
        self.preview_btn.clicked.connect(self.preview_selected_file)
        bottom_layout.addWidget(self.preview_btn)
        
        hint_label = QLabel("双击预览 | Delete 删除")
        hint_label.setObjectName("subtitleLabel")
        bottom_layout.addWidget(hint_label)
        
        layout.addLayout(bottom_layout)
        
        return panel

    def create_right_panel(self) -> QWidget:
        """创建右侧设置面板"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 使用 AnimatedStackedWidget 切换不同的设置面板
        self.settings_stack = AnimatedStackedWidget()
        
        # 图片转换设置面板
        image_settings = self.create_image_settings()
        self.settings_stack.addWidget(image_settings)
        
        # MPKG 转换设置面板
        mpkg_settings = self.create_mpkg_settings()
        self.settings_stack.addWidget(mpkg_settings)
        
        layout.addWidget(self.settings_stack)
        
        return panel

    def create_image_settings(self) -> QWidget:
        """创建图片转换设置面板"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("图片转换设置")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #f5f5f7;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 8, 0)
        scroll_layout.setSpacing(20) # 增加卡片间的间距
        
        # 输出格式卡片
        format_card = SettingsCard("输出格式")
        format_layout = QHBoxLayout()
        format_layout.setSpacing(12)
        
        format_label = QLabel("选择格式")
        format_label.setMinimumWidth(80)
        format_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(OUTPUT_FORMATS)
        self.format_combo.setCurrentText("png")
        self.format_combo.setMinimumWidth(120)
        format_layout.addWidget(self.format_combo, 1)
        
        format_layout.addStretch()
        format_card.addLayout(format_layout)
        scroll_layout.addWidget(format_card)
        
        # 尺寸调整卡片
        size_card = SettingsCard("尺寸调整")
        self.resize_check = QCheckBox("启用尺寸调整")
        size_card.main_layout.insertWidget(1, self.resize_check) # 插入到标题下，内容上
        
        size_layout = QHBoxLayout()
        size_layout.setSpacing(12)
        
        width_label = QLabel("宽度")
        width_label.setMinimumWidth(50)
        size_layout.addWidget(width_label)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(800)
        self.width_spin.setSuffix(" px")
        self.width_spin.setMinimumWidth(100)
        size_layout.addWidget(self.width_spin)
        
        height_label = QLabel("高度")
        height_label.setMinimumWidth(50)
        size_layout.addWidget(height_label)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(600)
        self.height_spin.setSuffix(" px")
        self.height_spin.setMinimumWidth(100)
        size_layout.addWidget(self.height_spin)
        
        self.keep_ratio_check = QCheckBox("保持比例")
        self.keep_ratio_check.setChecked(True)
        size_layout.addWidget(self.keep_ratio_check)
        
        size_layout.addStretch()
        size_card.addLayout(size_layout)
        scroll_layout.addWidget(size_card)
        
        def update_size_enabled(checked):
            enabled = checked == Qt.Checked
            self.width_spin.setEnabled(enabled)
            self.height_spin.setEnabled(enabled)
            self.keep_ratio_check.setEnabled(enabled)
        
        self.resize_check.stateChanged.connect(update_size_enabled)
        update_size_enabled(Qt.Unchecked)
        
        # 图片裁剪卡片
        crop_card = SettingsCard("图片裁剪")
        self.crop_check = QCheckBox("启用裁剪")
        crop_card.main_layout.insertWidget(1, self.crop_check)
        
        crop_hint = QLabel("双击文件预览并设置裁剪区域")
        crop_hint.setObjectName("subtitleLabel")
        crop_card.addWidget(crop_hint)
        
        self.crop_info_label = QLabel("未设置裁剪区域")
        self.crop_info_label.setStyleSheet("""
            background: #f5f5f7;
            border-radius: 8px;
            padding: 10px;
            color: #86868b;
        """)
        crop_card.addWidget(self.crop_info_label)
        scroll_layout.addWidget(crop_card)
        
        def update_crop_enabled(checked):
            enabled = checked == Qt.Checked
            crop_hint.setEnabled(enabled)
            self.crop_info_label.setEnabled(enabled)
        
        self.crop_check.stateChanged.connect(update_crop_enabled)
        update_crop_enabled(Qt.Unchecked)
        
        # 压缩质量卡片
        quality_card = SettingsCard("压缩质量")
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(12)
        
        quality_label_left = QLabel("质量")
        quality_label_left.setMinimumWidth(50)
        slider_layout.addWidget(quality_label_left)
        
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(85)
        slider_layout.addWidget(self.quality_slider, 1)
        
        self.quality_label = QLabel("85%")
        self.quality_label.setStyleSheet("font-weight: 600; color: #007aff; min-width: 50px;")
        slider_layout.addWidget(self.quality_label)
        
        quality_card.addLayout(slider_layout)
        
        quality_hint = QLabel("仅对 JPG/WebP 格式有效")
        quality_hint.setObjectName("subtitleLabel")
        quality_card.addWidget(quality_hint)
        scroll_layout.addWidget(quality_card)
        
        # 输出目录卡片
        output_card = SettingsCard("输出目录")
        output_layout = QHBoxLayout()
        output_layout.setSpacing(12)
        
        output_label = QLabel("目录")
        output_label.setMinimumWidth(50)
        output_layout.addWidget(output_label)
        
        self.output_path_label = QLabel("未选择")
        self.output_path_label.setStyleSheet("""
            background: #f5f5f7;
            border-radius: 8px;
            padding: 10px;
            color: #86868b;
        """)
        output_layout.addWidget(self.output_path_label, 1)
        
        browse_btn = ModernButton("浏览")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_btn)
        output_card.addLayout(output_layout)
        scroll_layout.addWidget(output_card)
        
        # 进度区域
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(12) # 确保有高度
        scroll_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("subtitleLabel")
        scroll_layout.addWidget(self.status_label)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
        
        # 转换按钮
        self.image_convert_btn = ModernButton("开始转换", is_primary=True)
        self.image_convert_btn.clicked.connect(self.start_image_convert)
        main_layout.addWidget(self.image_convert_btn)
        
        return main_widget

    def create_mpkg_settings(self) -> QWidget:
        """创建 MPKG 转换设置面板"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("MPKG 转 MP4")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #f5f5f7;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 8, 0)
        scroll_layout.setSpacing(20)
        
        # 说明卡片
        info_card = SettingsCard("关于 MPKG 格式")
        info_text = QLabel(
            "MPKG 是 Wallpaper Engine 的壁纸包格式，\n"
            "内部包含视频文件。此工具可以提取其中的 MP4 视频。"
        )
        info_text.setWordWrap(True)
        info_text.setObjectName("subtitleLabel")
        info_card.addWidget(info_text)
        scroll_layout.addWidget(info_card)
        
        # 输出目录卡片
        output_card = SettingsCard("输出目录")
        output_layout = QHBoxLayout()
        output_layout.setSpacing(12)
        
        output_label = QLabel("目录")
        output_label.setMinimumWidth(50)
        output_layout.addWidget(output_label)
        
        self.mpkg_output_path_label = QLabel("未选择")
        self.mpkg_output_path_label.setStyleSheet("""
            background: #f5f5f7;
            border-radius: 8px;
            padding: 10px;
            color: #86868b;
        """)
        output_layout.addWidget(self.mpkg_output_path_label, 1)
        
        browse_btn = ModernButton("浏览")
        browse_btn.clicked.connect(self.browse_mpkg_output_dir)
        output_layout.addWidget(browse_btn)
        output_card.addLayout(output_layout)
        scroll_layout.addWidget(output_card)
        
        # 进度区域
        self.mpkg_progress_bar = QProgressBar()
        self.mpkg_progress_bar.setVisible(False)
        scroll_layout.addWidget(self.mpkg_progress_bar)
        
        self.mpkg_status_label = QLabel()
        self.mpkg_status_label.setAlignment(Qt.AlignCenter)
        self.mpkg_status_label.setObjectName("subtitleLabel")
        scroll_layout.addWidget(self.mpkg_status_label)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
        
        # 转换按钮
        self.mpkg_convert_btn = ModernButton("开始提取", is_primary=True)
        self.mpkg_convert_btn.clicked.connect(self.start_mpkg_convert)
        main_layout.addWidget(self.mpkg_convert_btn)
        
        return main_widget

    def apply_shadow_effects(self):
        """应用轻量级阴影效果"""
        # 简约风格使用更轻的阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.main_container.setGraphicsEffect(shadow)

    def connect_signals(self):
        """连接信号"""
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(f"{v}%")
        )
        self.mode_group.buttonClicked.connect(self.on_mode_changed)

    def on_mode_changed(self, button):
        """模式切换"""
        if button == self.image_mode_btn:
            self.settings_stack.setCurrentIndex(0)
            self.file_list.set_mode('image')
            self.title_label.setText("待转换图片")
            self.subtitle_label.setText("拖拽图片文件或文件夹到下方区域，或点击按钮添加")
            self.preview_btn.setVisible(True)
            # 切换到图片模式的文件列表
            self.refresh_file_list_for_mode()
        else:
            self.settings_stack.setCurrentIndex(1)
            self.file_list.set_mode('mpkg')
            self.title_label.setText("待转换 MPKG 文件")
            self.subtitle_label.setText("拖拽 MPKG 文件或文件夹到下方区域，或点击按钮添加")
            self.preview_btn.setVisible(False)
            # 切换到 MPKG 模式的文件列表
            self.refresh_file_list_for_mode()

    def refresh_file_list_for_mode(self):
        """根据模式刷新文件列表显示"""
        self.file_list.clear()
        if self.image_mode_btn.isChecked():
            files = self.image_files
            for filepath in files:
                info = get_image_info(filepath)
                if info:
                    item_text = f"{os.path.basename(filepath)}  •  {info['width']}×{info['height']}  •  {format_file_size(info['size'])}"
                else:
                    item_text = f"{os.path.basename(filepath)}"
                self.file_list.addItem(item_text)
        else:
            files = self.mpkg_files
            for filepath in files:
                size = os.path.getsize(filepath)
                item_text = f"{os.path.basename(filepath)}  •  {format_file_size(size)}"
                self.file_list.addItem(item_text)
        self.update_file_count()

    def add_files(self):
        """添加文件对话框"""
        if self.image_mode_btn.isChecked():
            filter_str = "图片文件 (*" + " *".join(READABLE_EXTENSIONS) + ")"
            files, _ = QFileDialog.getOpenFileNames(
                self, "选择图片文件", "", filter_str
            )
        else:
            filter_str = "MPKG 文件 (*.mpkg)"
            files, _ = QFileDialog.getOpenFileNames(
                self, "选择 MPKG 文件", "", filter_str
            )
        if files:
            self.add_files_to_list(files)

    def add_folder(self):
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    if self.image_mode_btn.isChecked():
                        if is_supported_file(filepath):
                            files.append(filepath)
                    else:
                        if is_mpkg_file(filepath):
                            files.append(filepath)
            if files:
                self.add_files_to_list(files)

    def add_files_to_list(self, files: List[str]):
        """添加文件到列表"""
        is_image_mode = self.image_mode_btn.isChecked()
        target_list = self.image_files if is_image_mode else self.mpkg_files
        
        new_items = []
        for filepath in files:
            if filepath not in target_list:
                target_list.append(filepath)
                if is_image_mode:
                    info = get_image_info(filepath)
                    if info:
                        item_text = f"{os.path.basename(filepath)}  •  {info['width']}×{info['height']}  •  {format_file_size(info['size'])}"
                    else:
                        item_text = f"{os.path.basename(filepath)}"
                else:
                    size = os.path.getsize(filepath)
                    item_text = f"{os.path.basename(filepath)}  •  {format_file_size(size)}"
                
                item = QListWidgetItem(item_text)
                self.file_list.addItem(item)
                new_items.append(item)
        
        # 为新项添加渐入动画
        self._animate_new_items(new_items)
        self.update_file_count()

    def _animate_new_items(self, items):
        """为新添加的项目添加淡入动画"""
        for i, item in enumerate(items):
            # 创建透明度效果
            effect = QGraphicsOpacityEffect(item.listWidget())
            item.listWidget().setItemWidget(item, QWidget())  # 临时widget
            
            # 创建淡入动画
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(200)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # 延迟启动，创建级联效果
            QTimer.singleShot(i * 30, animation.start)

    def clear_files(self):
        """清空文件列表"""
        if self.image_mode_btn.isChecked():
            self.image_files.clear()
            self.crop_rects.clear()
            self.update_crop_info()
        else:
            self.mpkg_files.clear()
        self.file_list.clear()
        self.update_file_count()
    
    def preview_file(self, item):
        """双击预览文件"""
        if not self.image_mode_btn.isChecked():
            return
        row = self.file_list.row(item)
        if 0 <= row < len(self.image_files):
            self._show_preview_dialog(self.image_files[row])
    
    def preview_selected_file(self):
        """预览选中的文件"""
        if not self.image_mode_btn.isChecked():
            return
        selected = self.file_list.currentRow()
        if 0 <= selected < len(self.image_files):
            self._show_preview_dialog(self.image_files[selected])
        else:
            QMessageBox.information(self, "提示", "请先选择一个文件")
    
    def _show_preview_dialog(self, filepath: str):
        """显示预览对话框"""
        try:
            dialog = PreviewDialog(filepath, self)
            
            # 如果已有裁剪区域，设置到对话框
            if filepath in self.crop_rects:
                dialog.crop_widget.set_crop_rect(self.crop_rects[filepath])
            
            if dialog.exec_() == PreviewDialog.Accepted:
                crop_rect = dialog.get_crop_rect()
                if crop_rect and crop_rect.isValid():
                    # 保存裁剪区域
                    self.crop_rects[filepath] = crop_rect
                    # 自动勾选启用裁剪
                    self.crop_check.setChecked(True)
                    self.update_crop_info()
                    
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))
    
    def update_crop_info(self):
        """更新裁剪信息显示"""
        if self.crop_rects:
            count = len(self.crop_rects)
            self.crop_info_label.setText(f"已设置 {count} 个文件的裁剪区域")
            self.crop_info_label.setStyleSheet("""
                background: #e8f5e9;
                border-radius: 8px;
                padding: 10px;
                color: #2e7d32;
            """)
        else:
            self.crop_info_label.setText("未设置裁剪区域")
            self.crop_info_label.setStyleSheet("""
                background: #f5f5f7;
                border-radius: 8px;
                padding: 10px;
                color: #86868b;
            """)

    def update_file_count(self):
        """更新文件计数"""
        if self.image_mode_btn.isChecked():
            count = len(self.image_files)
        else:
            count = len(self.mpkg_files)
        self.file_count_label.setText(f"共 {count} 个文件")

    def browse_output_dir(self):
        """浏览输出目录"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.output_path_label.setText(folder)
            self.output_path_label.setStyleSheet("""
                background: #e8f5e9;
                border-radius: 8px;
                padding: 10px;
                color: #2e7d32;
            """)

    def browse_mpkg_output_dir(self):
        """浏览 MPKG 输出目录"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.mpkg_output_path_label.setText(folder)
            self.mpkg_output_path_label.setStyleSheet("""
                background: #e8f5e9;
                border-radius: 8px;
                padding: 10px;
                color: #2e7d32;
            """)

    def start_image_convert(self):
        """开始图片转换"""
        if not self.image_files:
            QMessageBox.warning(self, "提示", "请先添加要转换的图片文件")
            return
        
        output_dir = self.output_path_label.text()
        if output_dir == "未选择输出目录":
            QMessageBox.warning(self, "提示", "请选择输出目录")
            return
        
        output_format = self.format_combo.currentText()
        quality = self.quality_slider.value()
        
        resize = None
        if self.resize_check.isChecked():
            resize = (self.width_spin.value(), self.height_spin.value())
        
        keep_ratio = self.keep_ratio_check.isChecked()
        
        # 处理裁剪区域
        crop_rects = {}
        if self.crop_check.isChecked() and self.crop_rects:
            for filepath, rect in self.crop_rects.items():
                crop_rects[filepath] = (rect.left(), rect.top(), rect.right(), rect.bottom())
        
        self.image_convert_btn.setEnabled(False)
        self.image_convert_btn.setText("转换中...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.image_files))
        self.status_label.setText("正在准备转换...")
        
        self.worker = ConvertWorker(
            self.image_files, output_dir, output_format, quality, resize, keep_ratio, crop_rects
        )
        self.worker.progress.connect(self.on_image_progress)
        self.worker.finished.connect(self.on_image_finished)
        self.worker.start()

    def on_image_progress(self, current: int, total: int, message: str):
        """图片转换进度更新（带动画）"""
        # 使用动画更新进度条
        if hasattr(self, '_progress_animation'):
            self._progress_animation.stop()
        
        self._progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self._progress_animation.setDuration(200)
        self._progress_animation.setStartValue(self.progress_bar.value())
        self._progress_animation.setEndValue(current)
        self._progress_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._progress_animation.start()
        
        percent = int(current / total * 100) if total > 0 else 0
        self.status_label.setText(f"正在处理 {current}/{total} ({percent}%)")

    def on_image_finished(self, success: int, fail: int, errors: List[str]):
        """图片转换完成"""
        self.image_convert_btn.setEnabled(True)
        self.image_convert_btn.setText("开始转换")
        self.progress_bar.setVisible(False)
        
        if fail == 0:
            self.status_label.setText(f"✓ 转换完成！成功处理 {success} 个文件")
            self.status_label.setStyleSheet("color: #2e7d32; font-size: 13px; font-weight: 600;")
            QMessageBox.information(self, "完成", f"成功转换 {success} 个文件！")
        else:
            self.status_label.setText(f"完成：成功 {success}，失败 {fail}")
            self.status_label.setStyleSheet("color: #f57c00; font-size: 13px; font-weight: 600;")
            error_msg = f"成功: {success}, 失败: {fail}\n\n失败原因:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... 还有 {len(errors) - 10} 个错误"
            QMessageBox.warning(self, "完成", error_msg)

    def start_mpkg_convert(self):
        """开始 MPKG 转换"""
        if not self.mpkg_files:
            QMessageBox.warning(self, "提示", "请先添加要转换的 MPKG 文件")
            return
        
        output_dir = self.mpkg_output_path_label.text()
        if output_dir == "未选择":
            QMessageBox.warning(self, "提示", "请选择输出目录")
            return
        
        self.mpkg_convert_btn.setEnabled(False)
        self.mpkg_convert_btn.setText("提取中...")
        self.mpkg_progress_bar.setVisible(True)
        self.mpkg_progress_bar.setValue(0)
        self.mpkg_progress_bar.setMaximum(len(self.mpkg_files))
        self.mpkg_status_label.setText("正在准备提取...")
        
        self.worker = MPKGConvertWorker(self.mpkg_files, output_dir)
        self.worker.progress.connect(self.on_mpkg_progress)
        self.worker.finished.connect(self.on_mpkg_finished)
        self.worker.start()

    def on_mpkg_progress(self, current: int, total: int, message: str):
        """MPKG 转换进度更新（带动画）"""
        # 使用动画更新进度条
        if hasattr(self, '_mpkg_progress_animation'):
            self._mpkg_progress_animation.stop()
        
        self._mpkg_progress_animation = QPropertyAnimation(self.mpkg_progress_bar, b"value")
        self._mpkg_progress_animation.setDuration(200)
        self._mpkg_progress_animation.setStartValue(self.mpkg_progress_bar.value())
        self._mpkg_progress_animation.setEndValue(current)
        self._mpkg_progress_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._mpkg_progress_animation.start()
        
        percent = int(current / total * 100) if total > 0 else 0
        self.mpkg_status_label.setText(f"正在处理 {current}/{total} ({percent}%) - {message}")

    def on_mpkg_finished(self, success: int, fail: int, errors: List[str]):
        """MPKG 转换完成"""
        self.mpkg_convert_btn.setEnabled(True)
        self.mpkg_convert_btn.setText("开始提取")
        self.mpkg_progress_bar.setVisible(False)
        
        if fail == 0:
            self.mpkg_status_label.setText(f"✓ 提取完成！成功处理 {success} 个文件")
            self.mpkg_status_label.setStyleSheet("color: #2e7d32; font-size: 13px; font-weight: 600;")
            QMessageBox.information(self, "完成", f"成功提取 {success} 个 MP4 文件！")
        else:
            self.mpkg_status_label.setText(f"完成：成功 {success}，失败 {fail}")
            self.mpkg_status_label.setStyleSheet("color: #f57c00; font-size: 13px; font-weight: 600;")
            error_msg = f"成功: {success}, 失败: {fail}\n\n失败原因:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... 还有 {len(errors) - 10} 个错误"
            QMessageBox.warning(self, "完成", error_msg)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 简约启动画面
    splash_w, splash_h = 360, 180
    splash_pix = QPixmap(splash_w, splash_h)
    splash_pix.fill(Qt.transparent)
    
    painter = QPainter(splash_pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    
    # 绘制背景 - 简约白色
    bg_path = QPainterPath()
    bg_path.addRoundedRect(0, 0, splash_w, splash_h, 12, 12)
    painter.fillPath(bg_path, QBrush(QColor(255, 255, 255)))
    
    # 绘制边框
    painter.setPen(QPen(QColor(229, 229, 234), 1))
    painter.drawRoundedRect(0, 0, splash_w, splash_h, 12, 12)
    
    # 绘制主标题
    painter.setPen(QColor(29, 29, 31))
    painter.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
    painter.drawText(splash_pix.rect().adjusted(0, -20, 0, 0), Qt.AlignCenter, "格式转换工具")
    
    # 绘制副标题
    painter.setPen(QColor(134, 134, 139))
    painter.setFont(QFont("Microsoft YaHei", 11))
    painter.drawText(splash_pix.rect().adjusted(0, 30, 0, 0), Qt.AlignCenter, "Converter & Extractor")
    
    painter.end()
    
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.show()
    
    # 应用现代化样式
    app.setStyleSheet(MODERN_STYLE)
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 简化启动流程
    def show_main():
        window = MainWindow()
        window.show()
        splash.finish(window)

    QTimer.singleShot(600, show_main)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
