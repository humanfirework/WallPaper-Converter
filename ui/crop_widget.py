"""
可拖拽裁剪框组件
支持拖拽调整裁剪区域大小和位置，支持缩放预览
"""
from PyQt5.QtWidgets import QWidget, QRubberBand
from PyQt5.QtCore import Qt, QRect, QRectF, QPoint, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QTransform, QPainterPath


class CropWidget(QWidget):
    """可拖拽裁剪组件"""
    
    # 缩放因子变化信号
    zoom_changed = pyqtSignal(float)
    
    # 边缘和角落检测距离
    EDGE_MARGIN = 10
    
    # 拖拽模式
    DRAG_NONE = 0
    DRAG_MOVE = 1
    DRAG_TOP = 2
    DRAG_BOTTOM = 3
    DRAG_LEFT = 4
    DRAG_RIGHT = 5
    DRAG_TOP_LEFT = 6
    DRAG_TOP_RIGHT = 7
    DRAG_BOTTOM_LEFT = 8
    DRAG_BOTTOM_RIGHT = 9
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 原始图片
        self.original_pixmap = None
        # 当前显示的图片（缩放后）
        self.pixmap = None
        self.image_rect = QRect()
        
        # 缩放相关
        self.base_scale_factor = 1.0  # 基础缩放（适应窗口）
        self.zoom_factor = 1.0  # 用户缩放倍数
        self.min_zoom = 0.1  # 最小缩放
        self.max_zoom = 5.0  # 最大缩放
        
        # 裁剪区域 (相对于原图的坐标)
        self.crop_rect = QRect()
        
        # 拖拽状态
        self.drag_mode = self.DRAG_NONE
        self.drag_start_pos = QPoint()
        self.drag_start_rect = QRect()
        
        # 最小裁剪尺寸
        self.min_crop_size = 50
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 设置固定比例 (None表示自由比例)
        self.aspect_ratio = None
        
        # 防抖定时器 - 避免频繁重绘
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_update_display)
        
    def set_image(self, pixmap: QPixmap, scale_factor: float = 1.0):
        """设置要显示的图片"""
        if pixmap is None or pixmap.isNull():
            self.original_pixmap = None
            self.pixmap = None
            return
        
        self.original_pixmap = pixmap
        self.base_scale_factor = max(0.01, scale_factor)  # 确保缩放因子有效
        self.zoom_factor = 1.0
        
        self._update_display()
    
    def _update_display(self):
        """更新显示（优化版本）"""
        if not self.original_pixmap:
            return
        
        # 计算总缩放因子
        total_scale = self.base_scale_factor * self.zoom_factor
        
        # 缩放图片 - 使用FastTransformation提高性能
        if total_scale != 1.0:
            # 根据缩放比例选择变换质量
            transform_mode = Qt.SmoothTransformation if total_scale > 0.5 else Qt.FastTransformation
            self.pixmap = self.original_pixmap.scaled(
                int(self.original_pixmap.width() * total_scale),
                int(self.original_pixmap.height() * total_scale),
                Qt.KeepAspectRatio,
                transform_mode
            )
        else:
            self.pixmap = self.original_pixmap
        
        # 计算图片在widget中的显示区域
        img_size = self.pixmap.size()
        x = (self.width() - img_size.width()) // 2
        y = (self.height() - img_size.height()) // 2
        self.image_rect = QRect(QPoint(x, y), img_size)
        
        # 初始化裁剪区域为整个图片（如果还没有设置）
        if not self.crop_rect.isValid() and self.original_pixmap:
            self.crop_rect = QRect(0, 0, self.original_pixmap.width(), self.original_pixmap.height())
        
        self.update()
    
    def _delayed_update_display(self):
        """延迟更新显示（防抖）"""
        self._update_display()
    
    def get_zoom_factor(self) -> float:
        """获取当前缩放倍数"""
        return self.zoom_factor
    
    def zoom_in(self):
        """放大"""
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor = min(self.zoom_factor * 1.25, self.max_zoom)
            self._update_display()
            self.zoom_changed.emit(self.zoom_factor)
    
    def zoom_out(self):
        """缩小"""
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor = max(self.zoom_factor / 1.25, self.min_zoom)
            self._update_display()
            self.zoom_changed.emit(self.zoom_factor)
    
    def reset_zoom(self):
        """重置缩放"""
        self.zoom_factor = 1.0
        self._update_display()
        self.zoom_changed.emit(self.zoom_factor)
    
    def set_crop_rect(self, rect: QRect):
        """设置裁剪区域 (原图坐标)"""
        if self.original_pixmap:
            # 确保裁剪区域在图片范围内
            rect = rect.intersected(QRect(0, 0, self.original_pixmap.width(), self.original_pixmap.height()))
            self.crop_rect = rect
            self.update()
    
    def get_crop_rect(self) -> QRect:
        """获取裁剪区域 (原图坐标)"""
        return self.crop_rect
    
    def set_aspect_ratio(self, ratio: float = None):
        """设置固定宽高比 (None为自由比例)"""
        self.aspect_ratio = ratio
        if ratio and self.crop_rect.isValid() and self.original_pixmap:
            # 调整当前裁剪区域以匹配比例
            w = self.crop_rect.width()
            h = int(w / ratio)
            if h > self.original_pixmap.height():
                h = self.original_pixmap.height()
                w = int(h * ratio)
            self.crop_rect.setSize(QSize(w, h))
            self.update()
    
    def _screen_to_image(self, pos: QPoint) -> QPoint:
        """屏幕坐标转图片坐标"""
        if not self.image_rect.isValid():
            return QPoint()
        total_scale = self.base_scale_factor * self.zoom_factor
        return QPoint(
            int((pos.x() - self.image_rect.x()) / total_scale),
            int((pos.y() - self.image_rect.y()) / total_scale)
        )
    
    def _image_to_screen(self, pos: QPoint) -> QPoint:
        """图片坐标转屏幕坐标"""
        if not self.image_rect.isValid():
            return QPoint()
        total_scale = self.base_scale_factor * self.zoom_factor
        return QPoint(
            int(pos.x() * total_scale + self.image_rect.x()),
            int(pos.y() * total_scale + self.image_rect.y())
        )
    
    def _get_screen_crop_rect(self) -> QRect:
        """获取屏幕坐标的裁剪区域"""
        top_left = self._image_to_screen(self.crop_rect.topLeft())
        bottom_right = self._image_to_screen(self.crop_rect.bottomRight())
        return QRect(top_left, bottom_right)
    
    def _get_drag_mode(self, pos: QPoint) -> int:
        """根据位置判断拖拽模式"""
        if not self.original_pixmap:
            return self.DRAG_NONE
            
        screen_crop = self._get_screen_crop_rect()
        
        # 检查是否在裁剪区域内
        if not screen_crop.contains(pos):
            return self.DRAG_NONE
        
        # 检测角落
        top = abs(pos.y() - screen_crop.top()) <= self.EDGE_MARGIN
        bottom = abs(pos.y() - screen_crop.bottom()) <= self.EDGE_MARGIN
        left = abs(pos.x() - screen_crop.left()) <= self.EDGE_MARGIN
        right = abs(pos.x() - screen_crop.right()) <= self.EDGE_MARGIN
        
        if top and left:
            return self.DRAG_TOP_LEFT
        if top and right:
            return self.DRAG_TOP_RIGHT
        if bottom and left:
            return self.DRAG_BOTTOM_LEFT
        if bottom and right:
            return self.DRAG_BOTTOM_RIGHT
        if top:
            return self.DRAG_TOP
        if bottom:
            return self.DRAG_BOTTOM
        if left:
            return self.DRAG_LEFT
        if right:
            return self.DRAG_RIGHT
        
        return self.DRAG_MOVE
    
    def _update_cursor(self, pos: QPoint):
        """更新鼠标光标"""
        mode = self._get_drag_mode(pos)
        
        cursors = {
            self.DRAG_NONE: Qt.ArrowCursor,
            self.DRAG_MOVE: Qt.SizeAllCursor,
            self.DRAG_TOP: Qt.SizeVerCursor,
            self.DRAG_BOTTOM: Qt.SizeVerCursor,
            self.DRAG_LEFT: Qt.SizeHorCursor,
            self.DRAG_RIGHT: Qt.SizeHorCursor,
            self.DRAG_TOP_LEFT: Qt.SizeFDiagCursor,
            self.DRAG_BOTTOM_RIGHT: Qt.SizeFDiagCursor,
            self.DRAG_TOP_RIGHT: Qt.SizeBDiagCursor,
            self.DRAG_BOTTOM_LEFT: Qt.SizeBDiagCursor,
        }
        
        self.setCursor(cursors.get(mode, Qt.ArrowCursor))
    
    def paintEvent(self, event):
        """绘制事件（优化版本）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        if not self.pixmap or self.pixmap.isNull():
            painter.fillRect(self.rect(), QColor(50, 50, 60))
            if not self.original_pixmap:
                painter.setPen(QColor(150, 150, 160))
                painter.drawText(self.rect(), Qt.AlignCenter, "请加载图片")
            return

        # 绘制图片
        painter.drawPixmap(self.image_rect, self.pixmap)
        
        # 绘制半透明遮罩
        screen_crop = self._get_screen_crop_rect()
        
        # 创建遮罩路径 - 使用组合绘制提高性能
        dark_color = QColor(0, 0, 0, 120)
        
        # 使用 QPainterPath 一次性绘制遮罩
        mask_path = QPainterPath()
        mask_path.addRect(QRectF(self.image_rect))
        crop_path = QPainterPath()
        crop_path.addRect(QRectF(screen_crop))
        mask_path = mask_path.subtracted(crop_path)
        painter.fillPath(mask_path, dark_color)
        
        # 绘制裁剪框边框
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(screen_crop)
        
        # 绘制九宫格辅助线
        pen = QPen(QColor(255, 255, 255, 150), 1, Qt.DashLine)
        painter.setPen(pen)
        
        # 垂直线 (三等分)
        third_w = screen_crop.width() // 3
        painter.drawLine(
            screen_crop.left() + third_w, screen_crop.top(),
            screen_crop.left() + third_w, screen_crop.bottom()
        )
        painter.drawLine(
            screen_crop.left() + third_w * 2, screen_crop.top(),
            screen_crop.left() + third_w * 2, screen_crop.bottom()
        )
        
        # 水平线 (三等分)
        third_h = screen_crop.height() // 3
        painter.drawLine(
            screen_crop.left(), screen_crop.top() + third_h,
            screen_crop.right(), screen_crop.top() + third_h
        )
        painter.drawLine(
            screen_crop.left(), screen_crop.top() + third_h * 2,
            screen_crop.right(), screen_crop.top() + third_h * 2
        )
        
        # 绘制角落拖拽手柄
        handle_size = 10
        handle_color = QColor(59, 130, 246)  # 蓝色
        painter.setBrush(QBrush(handle_color))
        painter.setPen(QPen(Qt.white, 1))
        
        corners = [
            screen_crop.topLeft(),
            screen_crop.topRight(),
            screen_crop.bottomLeft(),
            screen_crop.bottomRight(),
        ]
        
        for corner in corners:
            painter.drawRect(
                corner.x() - handle_size // 2,
                corner.y() - handle_size // 2,
                handle_size, handle_size
            )
        
        # 绘制边缘中点手柄
        edge_handles = [
            QPoint(screen_crop.left() + screen_crop.width() // 2, screen_crop.top()),
            QPoint(screen_crop.left() + screen_crop.width() // 2, screen_crop.bottom()),
            QPoint(screen_crop.left(), screen_crop.top() + screen_crop.height() // 2),
            QPoint(screen_crop.right(), screen_crop.top() + screen_crop.height() // 2),
        ]
        
        for handle in edge_handles:
            painter.drawRect(
                handle.x() - handle_size // 2,
                handle.y() - handle_size // 2,
                handle_size, handle_size
            )
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.LeftButton and self.original_pixmap:
            self.drag_mode = self._get_drag_mode(event.pos())
            self.drag_start_pos = event.pos()
            self.drag_start_rect = QRect(self.crop_rect)
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.drag_mode != self.DRAG_NONE:
            self._perform_drag(event.pos())
        else:
            self._update_cursor(event.pos())
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        self.drag_mode = self.DRAG_NONE
    
    def _perform_drag(self, pos: QPoint):
        """执行拖拽操作"""
        if not self.original_pixmap:
            return
        
        # 计算移动量 (图片坐标)
        total_scale = self.base_scale_factor * self.zoom_factor
        delta_screen = pos - self.drag_start_pos
        delta_image = QPoint(
            int(delta_screen.x() / total_scale),
            int(delta_screen.y() / total_scale)
        )
        
        new_rect = QRect(self.drag_start_rect)
        
        if self.drag_mode == self.DRAG_MOVE:
            # 移动整个裁剪框
            new_rect.translate(delta_image)
            # 确保在图片范围内
            if new_rect.left() < 0:
                new_rect.moveLeft(0)
            if new_rect.top() < 0:
                new_rect.moveTop(0)
            if new_rect.right() > self.original_pixmap.width():
                new_rect.moveRight(self.original_pixmap.width())
            if new_rect.bottom() > self.original_pixmap.height():
                new_rect.moveBottom(self.original_pixmap.height())
        
        else:
            # 调整大小
            if self.drag_mode in (self.DRAG_TOP, self.DRAG_TOP_LEFT, self.DRAG_TOP_RIGHT):
                new_top = self.drag_start_rect.top() + delta_image.y()
                if new_top < self.drag_start_rect.bottom() - self.min_crop_size:
                    new_rect.setTop(new_top)
            
            if self.drag_mode in (self.DRAG_BOTTOM, self.DRAG_BOTTOM_LEFT, self.DRAG_BOTTOM_RIGHT):
                new_bottom = self.drag_start_rect.bottom() + delta_image.y()
                if new_bottom > self.drag_start_rect.top() + self.min_crop_size:
                    new_rect.setBottom(new_bottom)
            
            if self.drag_mode in (self.DRAG_LEFT, self.DRAG_TOP_LEFT, self.DRAG_BOTTOM_LEFT):
                new_left = self.drag_start_rect.left() + delta_image.x()
                if new_left < self.drag_start_rect.right() - self.min_crop_size:
                    new_rect.setLeft(new_left)
            
            if self.drag_mode in (self.DRAG_RIGHT, self.DRAG_TOP_RIGHT, self.DRAG_BOTTOM_RIGHT):
                new_right = self.drag_start_rect.right() + delta_image.x()
                if new_right > self.drag_start_rect.left() + self.min_crop_size:
                    new_rect.setRight(new_right)
            
            # 保持宽高比
            if self.aspect_ratio:
                self._apply_aspect_ratio(new_rect)
        
        # 确保裁剪区域在图片范围内
        new_rect = new_rect.intersected(QRect(0, 0, self.original_pixmap.width(), self.original_pixmap.height()))
        
        # 确保最小尺寸
        if new_rect.width() < self.min_crop_size:
            new_rect.setWidth(self.min_crop_size)
        if new_rect.height() < self.min_crop_size:
            new_rect.setHeight(self.min_crop_size)
        
        self.crop_rect = new_rect
        self.update()
    
    def _apply_aspect_ratio(self, rect: QRect):
        """应用宽高比约束"""
        if not self.aspect_ratio:
            return
        
        current_ratio = rect.width() / rect.height() if rect.height() > 0 else 1
        
        if current_ratio > self.aspect_ratio:
            # 太宽，调整宽度
            new_width = int(rect.height() * self.aspect_ratio)
            if self.drag_mode in (self.DRAG_LEFT, self.DRAG_TOP_LEFT, self.DRAG_BOTTOM_LEFT):
                rect.setLeft(rect.right() - new_width)
            else:
                rect.setRight(rect.left() + new_width)
        else:
            # 太高，调整高度
            new_height = int(rect.width() / self.aspect_ratio)
            if self.drag_mode in (self.DRAG_TOP, self.DRAG_TOP_LEFT, self.DRAG_TOP_RIGHT):
                rect.setTop(rect.bottom() - new_height)
            else:
                rect.setBottom(rect.top() + new_height)
    
    def resizeEvent(self, event):
        """窗口大小改变时重新计算图片位置（带防抖）"""
        if self.original_pixmap:
            # 使用定时器防抖，避免频繁重绘
            self._resize_timer.start(50)  # 50ms 防抖延迟
        super().resizeEvent(event)
    
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 缩放"""
        if not self.original_pixmap:
            return
        
        # 获取滚轮方向
        delta = event.angleDelta().y()
        
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
