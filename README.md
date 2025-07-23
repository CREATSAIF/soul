# 🖼️ 图片批量水印工具

一个功能强大的图片批量水印处理工具，支持多种图片格式和水印模式。

## ✨ 主要特性

- 📸 **多格式支持**: JPEG, PNG, BMP, TIFF, WebP, GIF
- 🔤 **双重水印**: 支持文字水印和图片水印
- 🎯 **多种位置**: 平铺全图、对角线、居中、四角等
- ⚙️ **参数丰富**: 透明度、大小、旋转角度、间距等
- 📦 **批量处理**: 一次处理多张图片，支持递归目录
- 🔍 **预览模式**: 先预览效果再批量处理
- 🖥️ **双界面**: 命令行版本和图形界面版本
- 🎨 **高质量**: 保持原图质量，支持多种输出格式

## 🚀 快速开始

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 图形界面版本 (推荐)

```bash
python watermark_gui.py
```

### 命令行版本

```bash
# 基本用法 - 文字水印
python watermark_cli.py batch -i ./photos -o ./output -w "版权所有"

# 图片水印
python watermark_cli.py batch -i ./photos -o ./output -w logo.png

# 预览模式
python watermark_cli.py batch -i ./photos -o ./output -w "测试" --preview
```

### 功能演示

```bash
# 运行演示查看各种效果
python demo.py
```

## 📚 使用说明

### 🖥️ 图形界面使用

1. **启动程序**: `python watermark_gui.py`
2. **选择输入路径**: 选择包含图片的文件夹
3. **选择输出目录**: 选择处理后图片的保存位置
4. **设置水印**:
   - 文字水印: 直接输入文字内容
   - 图片水印: 选择水印图片文件
5. **调整参数**: 位置、透明度、大小比例、旋转角度等
6. **开始处理**: 点击"开始处理"按钮

### 💻 命令行使用

#### 基本命令

```bash
# 查看帮助
python watermark_cli.py --help

# 查看批量处理选项
python watermark_cli.py batch --help

# 查看支持的格式
python watermark_cli.py formats

# 查看使用示例
python watermark_cli.py examples
```

#### 常用示例

```bash
# 1. 基本文字水印 (平铺全图)
python watermark_cli.py batch \
  -i ./photos \
  -o ./output \
  -w "版权所有 © 2024"

# 2. 图片水印 (右下角)
python watermark_cli.py batch \
  -i ./photos \
  -o ./output \
  -w logo.png \
  --position bottom_right

# 3. 自定义参数
python watermark_cli.py batch \
  -i ./photos \
  -o ./output \
  -w "机密文档" \
  --position tile \
  --opacity 0.3 \
  --size 0.15 \
  --rotation 45 \
  --spacing 80

# 4. 递归处理子目录
python watermark_cli.py batch \
  -i ./photos \
  -o ./output \
  -w "水印" \
  --recursive

# 5. 处理单张图片
python watermark_cli.py single \
  -i photo.jpg \
  -o watermarked.jpg \
  -w "Sample"
```

## 🎯 水印位置说明

| 位置 | 说明 | 适用场景 |
|------|------|----------|
| `tile` | 平铺全图 | 防盗版保护 |
| `diagonal` | 对角线平铺 | 防盗版保护 |
| `center` | 居中显示 | logo展示 |
| `top_left` | 左上角 | 版权标识 |
| `top_right` | 右上角 | 版权标识 |
| `bottom_left` | 左下角 | 版权标识 |
| `bottom_right` | 右下角 | 版权标识 |

## ⚙️ 参数详解

### 基本参数

- **透明度 (opacity)**: 0.1-1.0，数值越小越透明
- **大小比例 (size)**: 0.05-1.0，相对于原图的大小比例
- **旋转角度 (rotation)**: -180到180度
- **水印间距 (spacing)**: 平铺模式下水印之间的间距(像素)
- **边距 (margin)**: 边角模式下水印到边缘的距离(像素)

### 高级选项

- **递归处理 (recursive)**: 处理子目录中的图片
- **预览模式 (preview)**: 只处理第一张图片用于预览
- **输出后缀 (suffix)**: 自定义输出文件名后缀

## 📋 支持的格式

### 输入格式

- **JPEG** (.jpg, .jpeg) - 最常用的图片格式
- **PNG** (.png) - 支持透明背景
- **BMP** (.bmp) - Windows位图格式
- **TIFF** (.tiff, .tif) - 高质量图片格式
- **WebP** (.webp) - Google现代格式
- **GIF** (.gif) - 动图格式(处理为静态图)

### 输出格式

输出格式与输入格式保持一致，自动保持原有质量参数。

## 🔧 安装与配置

### 系统要求

- Python 3.7+
- macOS / Linux / Windows

### 安装步骤

1. **克隆项目**:
   ```bash
   git clone <repository-url>
   cd watermark_tool
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**:
   ```bash
   # 图形界面
   python watermark_gui.py
   
   # 命令行
   python watermark_cli.py --help
   
   # 功能演示
   python demo.py
   ```

## 📁 项目结构

```
watermark_tool/
├── watermark_processor.py    # 核心处理引擎
├── watermark_cli.py         # 命令行界面
├── watermark_gui.py         # 图形界面
├── demo.py                  # 功能演示
├── requirements.txt         # Python依赖
└── README.md               # 项目说明
```

## 💡 使用技巧

### 最佳实践

1. **先用预览模式**: 处理大量图片前，先用 `--preview` 参数查看效果
2. **合理设置透明度**: 
   - 防盗版: 0.2-0.4 (较透明，不影响观感)
   - 版权标识: 0.6-0.8 (较明显)
3. **选择合适位置**:
   - 平铺模式适合防盗版
   - 角落模式适合版权标识
4. **调整水印大小**: 
   - 小图片: 0.3-0.5
   - 大图片: 0.1-0.2

### 性能优化

- 批量处理大量图片时，建议关闭预览模式
- 处理高分辨率图片时，可以适当减小水印大小比例
- 使用SSD存储可以显著提升处理速度

## ❓ 常见问题

### Q: 如何制作透明背景的水印图片？
A: 使用Photoshop、GIMP等工具制作PNG格式的透明背景图片。

### Q: 水印太淡看不清怎么办？
A: 增加透明度参数 (--opacity)，或选择对比度更高的颜色。

### Q: 如何批量处理不同文件夹的图片？
A: 使用 `--recursive` 参数可以递归处理子目录。

### Q: 处理后的图片质量下降？
A: 程序会自动保持原图质量参数，如需调整可以修改源码中的保存参数。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

---

**🎉 享受使用这个水印工具！如果有任何问题或建议，请随时联系。** 