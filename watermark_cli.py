#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import click
from pathlib import Path
from watermark_processor import WatermarkProcessor, WatermarkPosition
from colorama import init, Fore, Style

# 初始化colorama以支持跨平台彩色输出
init()

def print_logo():
    """打印工具Logo"""
    logo = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    🖼️  图片批量水印工具                      ║
║                   Image Watermark Tool                      ║
║                        作者: Shiro                          ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(logo)

def validate_path(ctx, param, value):
    """验证路径是否存在"""
    if value and not os.path.exists(value):
        raise click.BadParameter(f'路径不存在: {value}')
    return value

def validate_output_dir(ctx, param, value):
    """验证输出目录"""
    if value:
        # 如果目录不存在，尝试创建
        try:
            os.makedirs(value, exist_ok=True)
        except Exception as e:
            raise click.BadParameter(f'无法创建输出目录 {value}: {e}')
    return value

@click.group()
@click.version_option("1.0.0")
def cli():
    """图片批量水印工具 - 支持多种格式，多种水印模式"""
    print_logo()

@cli.command()
@click.option('--input', '-i', 
              type=click.Path(exists=True), 
              required=True,
              help='输入图片文件或目录路径')
@click.option('--output', '-o', 
              type=click.Path(),
              required=True,
              callback=validate_output_dir,
              help='输出目录路径')
@click.option('--watermark', '-w', 
              required=True,
              help='水印内容：文字内容或水印图片路径')
@click.option('--position', '-p',
              type=click.Choice(['tile', 'diagonal', 'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right']),
              default='tile',
              help='水印位置 (默认: tile - 平铺全图)')
@click.option('--opacity', '-a',
              type=click.FloatRange(0.1, 1.0),
              default=0.5,
              help='水印透明度 (0.1-1.0, 默认: 0.5)')
@click.option('--size', '-s',
              type=click.FloatRange(0.05, 1.0),
              default=0.2,
              help='水印大小比例 (0.05-1.0, 默认: 0.2)')
@click.option('--rotation', '-r',
              type=click.IntRange(-180, 180),
              default=45,
              help='水印旋转角度 (-180到180度, 默认: 45)')
@click.option('--spacing',
              type=click.IntRange(0, 200),
              default=50,
              help='平铺模式下水印间距 (像素, 默认: 50)')
@click.option('--margin',
              type=click.IntRange(0, 100),
              default=20,
              help='边角模式下水印边距 (像素, 默认: 20)')
@click.option('--recursive', '-R',
              is_flag=True,
              help='递归处理子目录中的图片')
@click.option('--suffix',
              default='_watermarked',
              help='输出文件名后缀 (默认: _watermarked)')
@click.option('--font-size',
              type=int,
              help='文字水印字体大小 (默认根据图片大小自动调整)')
@click.option('--font-color',
              default='white',
              help='文字水印颜色 (默认: white)')
@click.option('--preview',
              is_flag=True,
              help='预览模式：只处理第一张图片用于预览效果')
def batch(input, output, watermark, position, opacity, size, rotation, 
          spacing, margin, recursive, suffix, font_size, font_color, preview):
    """批量给图片添加水印"""
    
    processor = WatermarkProcessor()
    
    # 转换位置参数
    position_map = {
        'tile': WatermarkPosition.TILE,
        'diagonal': WatermarkPosition.DIAGONAL,
        'center': WatermarkPosition.CENTER,
        'top_left': WatermarkPosition.TOP_LEFT,
        'top_right': WatermarkPosition.TOP_RIGHT,
        'bottom_left': WatermarkPosition.BOTTOM_LEFT,
        'bottom_right': WatermarkPosition.BOTTOM_RIGHT,
    }
    
    watermark_position = position_map[position]
    
    # 显示处理信息
    click.echo(f"\n{Fore.YELLOW}📋 处理参数:")
    click.echo(f"   输入路径: {input}")
    click.echo(f"   输出目录: {output}")
    click.echo(f"   水印内容: {watermark}")
    click.echo(f"   水印位置: {position}")
    click.echo(f"   透明度: {opacity}")
    click.echo(f"   大小比例: {size}")
    click.echo(f"   旋转角度: {rotation}°")
    if position in ['tile', 'diagonal']:
        click.echo(f"   水印间距: {spacing}px")
    else:
        click.echo(f"   边距: {margin}px")
    click.echo(f"   递归处理: {'是' if recursive else '否'}")
    click.echo(f"   预览模式: {'是' if preview else '否'}{Style.RESET_ALL}\n")
    
    # 获取图片文件列表
    image_files = processor.get_image_files(input, recursive)
    
    if not image_files:
        click.echo(f"{Fore.RED}❌ 在指定路径中没有找到支持的图片文件{Style.RESET_ALL}")
        return
    
    if preview:
        image_files = image_files[:1]
        click.echo(f"{Fore.BLUE}🔍 预览模式：只处理第一张图片{Style.RESET_ALL}")
    
    click.echo(f"{Fore.GREEN}📁 找到 {len(image_files)} 张图片{Style.RESET_ALL}")
    
    # 确认处理
    if not preview and len(image_files) > 1:
        if not click.confirm(f'\n确定要处理这 {len(image_files)} 张图片吗？'):
            click.echo(f"{Fore.YELLOW}⏹️  操作已取消{Style.RESET_ALL}")
            return
    
    # 准备参数
    kwargs = {
        'position': watermark_position,
        'opacity': opacity,
        'size_ratio': size,
        'rotation': rotation,
        'spacing': spacing,
        'margin': margin,
    }
    
    # 添加文字水印特定参数
    if not os.path.exists(watermark):  # 文字水印
        if font_size:
            kwargs['font_size'] = font_size
        
        # 解析颜色
        color_map = {
            'white': (255, 255, 255, int(255 * opacity)),
            'black': (0, 0, 0, int(255 * opacity)),
            'red': (255, 0, 0, int(255 * opacity)),
            'green': (0, 255, 0, int(255 * opacity)),
            'blue': (0, 0, 255, int(255 * opacity)),
        }
        kwargs['font_color'] = color_map.get(font_color.lower(), (255, 255, 255, int(255 * opacity)))
    
    try:
        # 开始批量处理
        click.echo(f"\n{Fore.CYAN}🚀 开始处理图片...{Style.RESET_ALL}")
        
        success_count, failed_count = processor.batch_process(
            input_path=input,
            output_dir=output,
            watermark=watermark,
            recursive=recursive,
            suffix=suffix,
            **kwargs
        )
        
        # 显示结果
        total = success_count + failed_count
        if success_count == total:
            click.echo(f"\n{Fore.GREEN}🎉 所有图片处理完成！")
            click.echo(f"   成功: {success_count} 张")
            click.echo(f"   输出目录: {output}{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.YELLOW}⚠️  处理完成（部分失败）")
            click.echo(f"   成功: {success_count} 张")
            click.echo(f"   失败: {failed_count} 张")
            click.echo(f"   输出目录: {output}{Style.RESET_ALL}")
        
        if preview:
            click.echo(f"\n{Fore.BLUE}💡 预览完成！如果效果满意，可以去掉 --preview 参数进行批量处理{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}⏹️  用户取消操作{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ 处理过程中出错: {e}{Style.RESET_ALL}")

@cli.command()
@click.option('--input', '-i',
              type=click.Path(exists=True),
              required=True,
              help='单张图片路径')
@click.option('--output', '-o',
              type=click.Path(),
              required=True,
              help='输出图片路径')
@click.option('--watermark', '-w',
              required=True,
              help='水印内容：文字内容或水印图片路径')
@click.option('--position', '-p',
              type=click.Choice(['tile', 'diagonal', 'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right']),
              default='tile',
              help='水印位置')
@click.option('--opacity', '-a',
              type=click.FloatRange(0.1, 1.0),
              default=0.5,
              help='水印透明度')
@click.option('--size', '-s',
              type=click.FloatRange(0.05, 1.0),
              default=0.2,
              help='水印大小比例')
@click.option('--rotation', '-r',
              type=click.IntRange(-180, 180),
              default=45,
              help='水印旋转角度')
def single(input, output, watermark, position, opacity, size, rotation):
    """处理单张图片"""
    
    processor = WatermarkProcessor()
    
    # 转换位置参数
    position_map = {
        'tile': WatermarkPosition.TILE,
        'diagonal': WatermarkPosition.DIAGONAL,
        'center': WatermarkPosition.CENTER,
        'top_left': WatermarkPosition.TOP_LEFT,
        'top_right': WatermarkPosition.TOP_RIGHT,
        'bottom_left': WatermarkPosition.BOTTOM_LEFT,
        'bottom_right': WatermarkPosition.BOTTOM_RIGHT,
    }
    
    watermark_position = position_map[position]
    
    click.echo(f"\n{Fore.CYAN}🖼️  处理单张图片...{Style.RESET_ALL}")
    click.echo(f"输入: {input}")
    click.echo(f"输出: {output}")
    
    try:
        success = processor.process_single_image(
            input_path=input,
            output_path=output,
            watermark=watermark,
            position=watermark_position,
            opacity=opacity,
            size_ratio=size,
            rotation=rotation
        )
        
        if success:
            click.echo(f"\n{Fore.GREEN}✅ 图片处理完成: {output}{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.RED}❌ 图片处理失败{Style.RESET_ALL}")
            
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ 处理出错: {e}{Style.RESET_ALL}")

@cli.command()
def formats():
    """显示支持的图片格式"""
    click.echo(f"\n{Fore.CYAN}📋 支持的图片格式:{Style.RESET_ALL}")
    
    formats_list = [
        ("JPEG", ".jpg, .jpeg", "最常用的图片格式"),
        ("PNG", ".png", "支持透明背景的格式"),
        ("BMP", ".bmp", "Windows位图格式"),
        ("TIFF", ".tiff, .tif", "高质量图片格式"),
        ("WebP", ".webp", "Google开发的现代格式"),
        ("GIF", ".gif", "动图格式（处理为静态图）"),
    ]
    
    for name, extensions, description in formats_list:
        click.echo(f"  {Fore.GREEN}• {name:<6}{Style.RESET_ALL} {extensions:<15} - {description}")
    
    click.echo(f"\n{Fore.YELLOW}💡 提示: 所有格式都支持批量处理{Style.RESET_ALL}")

@cli.command()
def examples():
    """显示使用示例"""
    click.echo(f"\n{Fore.CYAN}📚 使用示例:{Style.RESET_ALL}\n")
    
    examples_list = [
        {
            "title": "基本文字水印",
            "cmd": "python watermark_cli.py batch -i ./photos -o ./output -w '版权所有'",
            "desc": "给photos目录下的所有图片添加文字水印"
        },
        {
            "title": "图片水印平铺",
            "cmd": "python watermark_cli.py batch -i ./photos -o ./output -w logo.png --position tile",
            "desc": "使用logo.png作为水印平铺到所有图片上"
        },
        {
            "title": "调整透明度和大小",
            "cmd": "python watermark_cli.py batch -i ./photos -o ./output -w '机密' --opacity 0.3 --size 0.1",
            "desc": "添加半透明小尺寸文字水印"
        },
        {
            "title": "右下角水印",
            "cmd": "python watermark_cli.py batch -i ./photos -o ./output -w logo.png --position bottom_right",
            "desc": "在图片右下角添加logo水印"
        },
        {
            "title": "预览效果",
            "cmd": "python watermark_cli.py batch -i ./photos -o ./output -w '测试' --preview",
            "desc": "预览模式，只处理第一张图片查看效果"
        },
        {
            "title": "递归处理",
            "cmd": "python watermark_cli.py batch -i ./photos -o ./output -w '水印' --recursive",
            "desc": "递归处理子目录中的所有图片"
        },
        {
            "title": "处理单张图片",
            "cmd": "python watermark_cli.py single -i photo.jpg -o watermarked.jpg -w 'Sample'",
            "desc": "只处理单张图片"
        }
    ]
    
    for i, example in enumerate(examples_list, 1):
        click.echo(f"{Fore.GREEN}{i}. {example['title']}{Style.RESET_ALL}")
        click.echo(f"   {Fore.BLUE}{example['cmd']}{Style.RESET_ALL}")
        click.echo(f"   {example['desc']}\n")

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}⏹️  程序被用户中断{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ 程序出错: {e}{Style.RESET_ALL}")
        sys.exit(1) 