
一个简洁高效的壁纸格式转换工具，支持图片批量转换和 MPKG 视频提取。

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-orange)

## 功能特性

### 图片转换模式
- **多格式支持**：支持 PNG、JPG、JPEG、BMP、WebP 等常用图片格式
- **批量处理**：支持同时处理多个文件，效率高效
- **尺寸调整**：可自定义输出图片的宽度和高度
- **比例保持**：可选保持原图宽高比
- **质量压缩**：可调节输出图片质量
- **裁剪功能**：支持交互式裁剪，选择感兴趣的区域
- **实时预览**：转换前可预览裁剪效果

<p align="center">
  <img src="https://github.com/user-attachments/assets/28992528-089e-4a35-a939-4374c3841606" alt="开始界面" width="600"/>
</p>


### MPKG 视频提取模式
- **MPKG 解析**：解析 Wallpaper Engine 的壁纸包格式
- **视频提取**：从 MPKG 文件中提取 MP4 视频
- **批量处理**：支持批量提取多个文件

<p align="center">
   <img src="https://github.com/user-attachments/assets/4dd79e9e-c3e3-47a4-8d50-a8105342667f" alt="MPKG提取界面" width="600"/>
</p>

## 界面预览

应用采用现代化的 UI 设计，具有以下特点：
- 简洁直观的操作界面
- 清晰的功能分区
- 流畅的交互动效
- 响应式的布局设计

<p align="center">
   <img src="https://github.com/user-attachments/assets/4437edc4-41ea-4710-9b20-84343dbf2bb8" alt="预览图片界面" width="600"/>
</p>

## 安装指南

### 环境要求
- Windows 10/11 系统
- Python 3.8 或更高版本

### 安装步骤

1. **克隆或下载项目**
```bash
git clone https://github.com/yourusername/WallPaper-Converter.git
cd WallPaper-Converter
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
python main.py
```

## 使用方法

### 图片转换

1. 选择左侧「图片转换」模式
2. 点击「添加文件」或「添加文件夹」导入图片
3. 在右侧设置面板中：
   - 选择输出格式（PNG/JPG/BMP/WebP）
   - 可选：启用尺寸调整，设置宽度和高度
   - 可选：启用质量压缩，调节质量值
4. 点击「预览/裁剪」可对图片进行裁剪
5. 设置输出目录
6. 点击「开始转换」执行转换

### MPKG 视频提取

1. 选择左侧「MPKG 转 MP4」模式
2. 点击「添加文件」导入 MPKG 文件
3. 设置输出目录
4. 点击「开始提取」执行提取

## 项目结构

```
WallPaper-Converter/
├── main.py                 # 应用入口
├── requirements.txt        # Python 依赖
├── ui/                     # 用户界面模块
│   ├── main_window.py     # 主窗口
│   ├── preview_dialog.py  # 预览对话框
│   └── crop_widget.py     # 裁剪组件
└── core/                   # 核心功能模块
    ├── converter.py       # 图片转换器
    ├── image_utils.py     # 图片工具函数
    └── mpkg_converter.py  # MPKG 解析器
```

## 配置说明

应用配置存储在用户目录下：
- Windows：`%APPDATA%\WallPaperConverter\`
- 配置文件：`config.json`

## 常见问题

**Q: 转换后的图片模糊怎么办？**
A: 在设置中提高质量值（建议 85-95），或禁用尺寸调整保持原图分辨率。

**Q: MPKG 文件无法识别？**
A: 请确保文件是 Wallpaper Engine 的 MPKG 格式，非加密或损坏。

**Q: 批量处理的文件顺序可以调整吗？**
A: 可以，选中文件后使用「上移」「下移」按钮调整顺序。

## 开发指南

### 技术栈
- **GUI 框架**：PyQt5
- **图片处理**：Pillow (PIL)
- **构建工具**：PyInstaller

### 打包构建

1. **安装 PyInstaller**
```bash
pip install pyinstaller
```

2. **创建 spec 文件**（如需要）
参考 `build.spec.template` 创建 `build.spec`

3. **执行构建**
```bash
pyinstaller build.spec
```

4. **发布版本**
```bash
git tag v1.0.0
git push origin v1.0.0
```
推送标签后，GitHub Actions 将自动构建并发布。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 支持图片格式转换
- 支持 MPKG 视频提取
- 现代化 UI 设计

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

## 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [Pillow](https://python-pillow.org/) - 图片处理库
- [Wallpaper Engine](https://store.steampowered.com/app/431960/Wallpaper_Engine/) - 灵感来源

## 如果觉得不错，可以给我加个鸡腿，谢谢，嘻嘻:

<p align="center">
      <img src="https://github.com/user-attachments/assets/a6d824d8-e237-44f0-b933-91f4daa8da48" alt="支持一下" height="352" width="256"/>
</p>
