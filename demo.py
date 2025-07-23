#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PIL import Image
from watermark_processor import WatermarkProcessor, WatermarkPosition
import time

def create_sample_images():
    """创建一些示例图片用于演示"""
    sample_dir = "sample_images"
    os.makedirs(sample_dir, exist_ok=True)
    
    # 创建不同颜色的示例图片
    colors = [
        ("red", (255, 100, 100)),
        ("green", (100, 255, 100)),
        ("blue", (100, 100, 255)),
        ("yellow", (255, 255, 100)),
    ]
    
    for name, color in colors:
        img = Image.new('RGB', (800, 600), color)
        img.save(f"{sample_dir}/{name}_sample.jpg", quality=95)
    
    print(f"✅ 已创建 {len(colors)} 张示例图片在 {sample_dir} 目录")
    return sample_dir

def create_sample_watermark():
    """创建示例水印图片"""
    # 创建一个简单的半透明logo
    watermark = Image.new('RGBA', (200, 100), (0, 0, 0, 0))
    
    # 添加一些简单的图形
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(watermark)
    
    # 绘制矩形边框
    draw.rectangle([10, 10, 190, 90], outline=(255, 255, 255, 200), width=3)
    
    # 添加文字
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    except:
        font = ImageFont.load_default()
    
    text = "DEMO"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (200 - text_width) // 2
    y = (100 - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))
    
    watermark_path = "demo_watermark.png"
    watermark.save(watermark_path)
    print(f"✅ 已创建示例水印图片: {watermark_path}")
    return watermark_path

def demo_text_watermark(processor, input_dir, output_dir):
    """演示文字水印功能"""
    print("\n🔤 演示文字水印功能...")
    
    demos = [
        {
            "name": "平铺文字水印",
            "position": WatermarkPosition.TILE,
            "watermark": "版权所有 © 2024",
            "opacity": 0.3,
            "rotation": 45,
            "suffix": "_text_tile"
        },
        {
            "name": "右下角文字水印",
            "position": WatermarkPosition.BOTTOM_RIGHT,
            "watermark": "机密文档",
            "opacity": 0.7,
            "rotation": 0,
            "suffix": "_text_corner"
        },
        {
            "name": "居中文字水印",
            "position": WatermarkPosition.CENTER,
            "watermark": "样本图片",
            "opacity": 0.5,
            "rotation": -30,
            "suffix": "_text_center"
        }
    ]
    
    for demo in demos:
        print(f"  📝 {demo['name']}...")
        
        demo_output = os.path.join(output_dir, "text_watermark")
        os.makedirs(demo_output, exist_ok=True)
        
        success, failed = processor.batch_process(
            input_path=input_dir,
            output_dir=demo_output,
            watermark=demo['watermark'],
            position=demo['position'],
            opacity=demo['opacity'],
            rotation=demo['rotation'],
            suffix=demo['suffix']
        )
        
        print(f"     成功: {success} 张，失败: {failed} 张")
        time.sleep(1)

def demo_image_watermark(processor, input_dir, output_dir, watermark_path):
    """演示图片水印功能"""
    print("\n🖼️  演示图片水印功能...")
    
    demos = [
        {
            "name": "平铺logo水印",
            "position": WatermarkPosition.TILE,
            "opacity": 0.4,
            "size_ratio": 0.15,
            "rotation": 0,
            "spacing": 100,
            "suffix": "_logo_tile"
        },
        {
            "name": "对角线logo水印",
            "position": WatermarkPosition.DIAGONAL,
            "opacity": 0.3,
            "size_ratio": 0.12,
            "rotation": 45,
            "spacing": 80,
            "suffix": "_logo_diagonal"
        },
        {
            "name": "右下角logo",
            "position": WatermarkPosition.BOTTOM_RIGHT,
            "opacity": 0.8,
            "size_ratio": 0.2,
            "rotation": 0,
            "margin": 30,
            "suffix": "_logo_corner"
        }
    ]
    
    for demo in demos:
        print(f"  🏷️  {demo['name']}...")
        
        demo_output = os.path.join(output_dir, "image_watermark")
        os.makedirs(demo_output, exist_ok=True)
        
        success, failed = processor.batch_process(
            input_path=input_dir,
            output_dir=demo_output,
            watermark=watermark_path,
            **demo
        )
        
        print(f"     成功: {success} 张，失败: {failed} 张")
        time.sleep(1)

def demo_batch_processing(processor, input_dir, output_dir):
    """演示批量处理功能"""
    print("\n📦 演示批量处理功能...")
    
    # 创建更多示例图片用于批量处理
    batch_dir = os.path.join(input_dir, "batch_test")
    os.makedirs(batch_dir, exist_ok=True)
    
    # 创建不同尺寸的图片
    sizes = [(400, 300), (800, 600), (1200, 900), (600, 800)]
    
    for i, size in enumerate(sizes):
        img = Image.new('RGB', size, (100 + i * 30, 150 + i * 20, 200 + i * 10))
        img.save(f"{batch_dir}/batch_{i+1}_{size[0]}x{size[1]}.png")
    
    print(f"  📁 创建了 {len(sizes)} 张不同尺寸的图片")
    
    # 批量添加水印
    batch_output = os.path.join(output_dir, "batch_result")
    os.makedirs(batch_output, exist_ok=True)
    
    print("  🔄 开始批量处理...")
    success, failed = processor.batch_process(
        input_path=batch_dir,
        output_dir=batch_output,
        watermark="批量处理演示",
        position=WatermarkPosition.TILE,
        opacity=0.4,
        rotation=30,
        suffix="_batch_demo"
    )
    
    print(f"     批量处理完成: 成功 {success} 张，失败 {failed} 张")

def show_results(output_dir):
    """显示处理结果"""
    print(f"\n📋 处理结果统计:")
    
    total_files = 0
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp')):
                total_files += 1
    
    print(f"  📊 总共生成了 {total_files} 张水印图片")
    print(f"  📂 输出目录: {os.path.abspath(output_dir)}")
    
    # 显示目录结构
    print(f"\n📁 输出目录结构:")
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        sub_indent = ' ' * 2 * (level + 1)
        for file in sorted(files)[:5]:  # 只显示前5个文件
            print(f"{sub_indent}{file}")
        
        if len(files) > 5:
            print(f"{sub_indent}... 还有 {len(files) - 5} 个文件")

def main():
    """主演示函数"""
    print("🖼️  图片水印工具功能演示")
    print("=" * 50)
    
    # 初始化处理器
    processor = WatermarkProcessor()
    
    # 创建演示目录
    base_dir = "watermark_demo"
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 演示目录: {os.path.abspath(base_dir)}")
    
    try:
        # 1. 创建示例图片和水印
        sample_dir = create_sample_images()
        watermark_path = create_sample_watermark()
        
        # 2. 演示文字水印
        demo_text_watermark(processor, sample_dir, output_dir)
        
        # 3. 演示图片水印
        demo_image_watermark(processor, sample_dir, output_dir, watermark_path)
        
        # 4. 演示批量处理
        demo_batch_processing(processor, input_dir, output_dir)
        
        # 5. 显示结果
        show_results(output_dir)
        
        print(f"\n🎉 演示完成！")
        print(f"💡 提示: 您可以查看 {os.path.abspath(output_dir)} 目录中的结果图片")
        print(f"🔧 可以使用以下命令进行更多操作:")
        print(f"   • 命令行版本: python watermark_cli.py --help")
        print(f"   • 图形界面版本: python watermark_gui.py")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 