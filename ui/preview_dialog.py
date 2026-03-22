"""
图片预览和裁剪对话框
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QFrame, QSizePolicy, QMessageBox,
    QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPixmap, QFont

from .crop_widget import CropWidget


class PreviewDialog(QDialog):
    """图片预览和裁剪对话框"""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap = QPixmap(image_path)
        self.crop_rect = None  # 裁剪区域
        
        if self.original_pixmap.isNull():
            raise ValueError(f"无法加载图片: {image_path}")
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"预览 - {os.path.basename(self.image_path)}")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 顶部信息栏
        info_layout = QHBoxLayout()
        
        info_text = f"尺寸: {self.original_pixmap.width()} × {self.original_pixmap.height()} px"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155;")
        info_layout.addWidget(info_label)
        
        file_size = os.path.getsize(self.image_path)
        size_text = self._format_size(file_size)
        size_label = QLabel(f"大小: {size_text}")
        size_label.setStyleSheet("font-size: 14px; color: #64748b;")
        info_layout.addWidget(size_label)
        
        info_layout.addStretch()
        
        # 图片名称
        name_label = QLabel(os.path.basename(self.image_path))
        name_label.setStyleSheet("font-size: 13px; color: #64748b;")
        info_layout.addWidget(name_label)
        
        layout.addLayout(info_layout)
        
        # 裁剪控件区域
        crop_controls = self._create_crop_controls()
        layout.addWidget(crop_controls)
        
        # 图片预览区域
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 12px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        self.crop_widget = CropWidget()
        self.crop_widget.setMinimumHeight(400)
        preview_layout.addWidget(self.crop_widget)
        
        layout.addWidget(preview_frame, 1)
        
        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 裁剪信息显示
        self.crop_info_label = QLabel("拖拽调整裁剪区域")
        self.crop_info_label.setStyleSheet("color: #64748b; font-size: 13px;")
        bottom_layout.addWidget(self.crop_info_label)
        
        bottom_layout.addStretch()
        
        # 重置按钮
        reset_btn = QPushButton("重置裁剪")
        reset_btn.setObjectName("smallBtn")
        reset_btn.clicked.connect(self.reset_crop)
        bottom_layout.addWidget(reset_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("smallBtn")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)
        
        # 确认按钮
        confirm_btn = QPushButton("应用裁剪")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        confirm_btn.clicked.connect(self.accept_crop)
        bottom_layout.addWidget(confirm_btn)
        
        layout.addLayout(bottom_layout)
        
        # 加载图片到裁剪控件
        self._load_image()
        
        # 应用样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QPushButton#smallBtn {
                background-color: #f1f5f9;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #475569;
            }
            QPushButton#smallBtn:hover {
                background-color: #e2e8f0;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 100px;
            }
            QCheckBox {
                spacing: 8px;
                color: #475569;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                font-weight: 600;
                color: #334155;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                background-color: #ffffff;
            }
            QSpinBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 10px;
                min-width: 70px;
            }
            QLabel {
                color: #475569;
            }
        """)
    
    def _create_crop_controls(self) -> QGroupBox:
        """创建裁剪控制区域"""
        group = QGroupBox("裁剪设置")
        main_layout = QVBoxLayout(group)
        main_layout.setSpacing(12)
        
        # 第一行：宽高比预设
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        ratio_label = QLabel("宽高比:")
        ratio_label.setFixedWidth(55)
        row1.addWidget(ratio_label)
        
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems([
            "自由", "1:1 (正方形)", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"
        ])
        self.ratio_combo.setCurrentIndex(0)
        self.ratio_combo.setMinimumWidth(120)
        row1.addWidget(self.ratio_combo)
        
        row1.addStretch()
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        zoom_label.setFixedWidth(40)
        row1.addWidget(zoom_label)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(32, 28)
        zoom_out_btn.clicked.connect(self._zoom_out)
        row1.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet("font-weight: 600; color: #3b82f6;")
        row1.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(32, 28)
        zoom_in_btn.clicked.connect(self._zoom_in)
        row1.addWidget(zoom_in_btn)
        
        reset_zoom_btn = QPushButton("重置")
        reset_zoom_btn.setFixedSize(50, 28)
        reset_zoom_btn.clicked.connect(self._reset_zoom)
        row1.addWidget(reset_zoom_btn)
        
        main_layout.addLayout(row1)
        
        # 第二行：自定义尺寸
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        custom_label = QLabel("自定义尺寸:")
        custom_label.setFixedWidth(70)
        row2.addWidget(custom_label)

        width_label = QLabel("宽")
        width_label.setFixedWidth(20)
        row2.addWidget(width_label)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 10000)
        self.width_spin.setValue(self.original_pixmap.width())
        self.width_spin.setSuffix(" px")
        self.width_spin.setMinimumWidth(90)
        row2.addWidget(self.width_spin)

        height_label = QLabel("高")
        height_label.setFixedWidth(20)
        row2.addWidget(height_label)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 10000)
        self.height_spin.setValue(self.original_pixmap.height())
        self.height_spin.setSuffix(" px")
        self.height_spin.setMinimumWidth(90)
        row2.addWidget(self.height_spin)

        row2.addStretch()

        main_layout.addLayout(row2)
        
        return group
    
    def connect_signals(self):
        """连接信号"""
        self.ratio_combo.currentIndexChanged.connect(self._on_ratio_changed)
        self.width_spin.valueChanged.connect(self._on_size_changed)
        self.height_spin.valueChanged.connect(self._on_size_changed)
        self.crop_widget.zoom_changed.connect(self._update_zoom_label)
    
    def _load_image(self):
        """加载图片到裁剪控件"""
        # 检查图片是否有效
        if self.original_pixmap.isNull() or self.original_pixmap.width() <= 0 or self.original_pixmap.height() <= 0:
            raise ValueError("图片尺寸无效")
        
        # 计算缩放因子以适应显示区域
        max_width = 1000
        max_height = 500
        
        img_width = self.original_pixmap.width()
        img_height = self.original_pixmap.height()
        
        scale_w = max_width / img_width if img_width > max_width else 1.0
        scale_h = max_height / img_height if img_height > max_height else 1.0
        scale = min(scale_w, scale_h)
        
        # 传递原始图片给裁剪控件，由控件内部处理缩放显示
        # 这样 get_crop_rect() 返回的坐标才是相对于原图的正确坐标
        self.crop_widget.set_image(self.original_pixmap, scale)
        self._update_crop_info()
    
    def _on_ratio_changed(self, index):
        """宽高比改变"""
        ratios = {
            0: None,      # 自由
            1: 1.0,       # 1:1
            2: 4/3,       # 4:3
            3: 3/4,       # 3:4
            4: 16/9,      # 16:9
            5: 9/16,      # 9:16
            6: 3/2,       # 3:2
            7: 2/3,       # 2:3
        }
        
        ratio = ratios.get(index)
        self.crop_widget.set_aspect_ratio(ratio)
        self._update_crop_info()
    
    def _on_size_changed(self):
        """自定义尺寸改变"""
        # 暂时断开信号避免循环
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        
        w = self.width_spin.value()
        h = self.height_spin.value()
        
        # 设置裁剪区域
        crop_rect = QRect(0, 0, w, h)
        self.crop_widget.set_crop_rect(crop_rect)
        
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)
        self._update_crop_info()
    
    def _zoom_in(self):
        """放大"""
        self.crop_widget.zoom_in()
    
    def _zoom_out(self):
        """缩小"""
        self.crop_widget.zoom_out()
    
    def _reset_zoom(self):
        """重置缩放"""
        self.crop_widget.reset_zoom()
    
    def _update_zoom_label(self, factor: float):
        """更新缩放标签"""
        self.zoom_label.setText(f"{int(factor * 100)}%")
    
    def _update_crop_info(self):
        """更新裁剪信息显示"""
        rect = self.crop_widget.get_crop_rect()
        if rect.isValid():
            self.crop_info_label.setText(
                f"裁剪区域: {rect.width()} × {rect.height()} px "
                f"(位置: {rect.x()}, {rect.y()})"
            )
    
    def reset_crop(self):
        """重置裁剪区域"""
        self.ratio_combo.setCurrentIndex(0)  # 自由比例
        self.crop_widget.set_aspect_ratio(None)
        self.crop_widget.set_crop_rect(QRect(0, 0, self.original_pixmap.width(), self.original_pixmap.height()))
        self.width_spin.setValue(self.original_pixmap.width())
        self.height_spin.setValue(self.original_pixmap.height())
        self._update_crop_info()
    
    def accept_crop(self):
        """确认裁剪"""
        self.crop_rect = self.crop_widget.get_crop_rect()
        self.accept()
    
    def get_crop_rect(self) -> QRect:
        """获取裁剪区域"""
        return self.crop_rect
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
