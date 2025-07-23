#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
import cv2
from pathlib import Path
import math
from typing import List, Tuple, Optional, Union
from enum import Enum
from tqdm import tqdm
import logging

class WatermarkPosition(Enum):
    """水印位置枚举"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    TILE = "tile"  # 平铺全图
    DIAGONAL = "diagonal"  # 对角线平铺

class WatermarkProcessor:
    """图片水印处理器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    
    def __init__(self):
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('WatermarkProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        return Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS
    
    def get_image_files(self, input_path: str, recursive: bool = False) -> List[str]:
        """获取指定路径下的所有图片文件"""
        image_files = []
        
        if os.path.isfile(input_path):
            if self.is_supported_format(input_path):
                image_files.append(input_path)
        elif os.path.isdir(input_path):
            pattern = "**/*" if recursive else "*"
            for file_path in Path(input_path).glob(pattern):
                if file_path.is_file() and self.is_supported_format(str(file_path)):
                    image_files.append(str(file_path))
        
        return sorted(image_files)
    
    def create_text_watermark(
        self, 
        text: str, 
        size: Tuple[int, int], 
        font_size: int = 48,
        font_color: Tuple[int, int, int, int] = (255, 255, 255, 128),
        font_path: Optional[str] = None,
        rotation: int = 0
    ) -> Image.Image:
        """创建文字水印"""
        # 创建透明背景的图片
        watermark = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 加载字体
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 尝试使用系统默认字体
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
                except:
                    font = ImageFont.load_default()
        except Exception as e:
            self.logger.warning(f"无法加载字体，使用默认字体: {e}")
            font = ImageFont.load_default()
        
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算文字位置（居中）
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # 绘制文字
        draw.text((x, y), text, font=font, fill=font_color)
        
        # 旋转水印
        if rotation != 0:
            watermark = watermark.rotate(rotation, expand=True)
        
        return watermark
    
    def create_image_watermark(
        self, 
        watermark_path: str, 
        target_size: Optional[Tuple[int, int]] = None,
        opacity: float = 0.5,
        rotation: int = 0
    ) -> Image.Image:
        """创建图片水印"""
        try:
            watermark = Image.open(watermark_path)
            
            # 转换为RGBA模式以支持透明度
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            # 调整大小
            if target_size:
                watermark = watermark.resize(target_size, Image.Resampling.LANCZOS)
            
            # 调整透明度
            if opacity < 1.0:
                # 创建一个透明度蒙版
                alpha = watermark.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                watermark.putalpha(alpha)
            
            # 旋转水印
            if rotation != 0:
                watermark = watermark.rotate(rotation, expand=True)
            
            return watermark
            
        except Exception as e:
            self.logger.error(f"无法加载水印图片 {watermark_path}: {e}")
            raise
    
    def apply_watermark_tile(
        self, 
        image: Image.Image, 
        watermark: Image.Image, 
        spacing: int = 50,
        angle: int = 45
    ) -> Image.Image:
        """平铺水印到整个图片"""
        img_width, img_height = image.size
        wm_width, wm_height = watermark.size
        
        # 旋转水印
        if angle != 0:
            watermark = watermark.rotate(angle, expand=True)
            wm_width, wm_height = watermark.size
        
        # 创建结果图片
        result = image.copy()
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
        
        # 计算平铺参数
        step_x = wm_width + spacing
        step_y = wm_height + spacing
        
        # 平铺水印
        for y in range(-wm_height, img_height + wm_height, step_y):
            for x in range(-wm_width, img_width + wm_width, step_x):
                # 创建临时图片用于粘贴水印
                temp = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
                
                # 计算水印位置
                paste_x = x
                paste_y = y
                
                # 如果水印超出边界，只粘贴可见部分
                if paste_x < img_width and paste_y < img_height and \
                   paste_x + wm_width > 0 and paste_y + wm_height > 0:
                    try:
                        temp.paste(watermark, (paste_x, paste_y), watermark)
                        result = Image.alpha_composite(result, temp)
                    except Exception as e:
                        self.logger.warning(f"粘贴水印时出错: {e}")
                        continue
        
        return result
    
    def apply_watermark_position(
        self, 
        image: Image.Image, 
        watermark: Image.Image,
        position: WatermarkPosition,
        margin: int = 20
    ) -> Image.Image:
        """在指定位置应用水印"""
        img_width, img_height = image.size
        wm_width, wm_height = watermark.size
        
        # 创建结果图片
        result = image.copy()
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
        
        # 计算水印位置
        if position == WatermarkPosition.TOP_LEFT:
            x, y = margin, margin
        elif position == WatermarkPosition.TOP_RIGHT:
            x, y = img_width - wm_width - margin, margin
        elif position == WatermarkPosition.BOTTOM_LEFT:
            x, y = margin, img_height - wm_height - margin
        elif position == WatermarkPosition.BOTTOM_RIGHT:
            x, y = img_width - wm_width - margin, img_height - wm_height - margin
        elif position == WatermarkPosition.CENTER:
            x, y = (img_width - wm_width) // 2, (img_height - wm_height) // 2
        else:
            x, y = margin, margin
        
        # 创建临时图片用于粘贴水印
        temp = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        temp.paste(watermark, (x, y), watermark)
        
        # 合成图片
        result = Image.alpha_composite(result, temp)
        
        return result
    
    def process_single_image(
        self,
        input_path: str,
        output_path: str,
        watermark: Union[str, Image.Image],
        position: WatermarkPosition = WatermarkPosition.TILE,
        opacity: float = 0.5,
        size_ratio: float = 0.2,
        rotation: int = 45,
        spacing: int = 50,
        margin: int = 20,
        **kwargs
    ) -> bool:
        """处理单张图片"""
        try:
            # 打开原图
            with Image.open(input_path) as image:
                original_mode = image.mode
                
                # 转换为RGBA模式处理
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # 创建或加载水印
                if isinstance(watermark, str):
                    if os.path.exists(watermark):
                        # 图片水印
                        img_width, img_height = image.size
                        wm_size = (
                            int(img_width * size_ratio),
                            int(img_height * size_ratio)
                        )
                        wm = self.create_image_watermark(
                            watermark, wm_size, opacity, rotation
                        )
                    else:
                        # 文字水印
                        font_size = int(min(image.size) * 0.05)  # 根据图片大小调整字体
                        wm = self.create_text_watermark(
                            watermark, 
                            image.size, 
                            font_size=font_size,
                            font_color=(255, 255, 255, int(255 * opacity)),
                            rotation=rotation
                        )
                else:
                    wm = watermark
                
                # 应用水印
                if position == WatermarkPosition.TILE or position == WatermarkPosition.DIAGONAL:
                    angle = rotation if position == WatermarkPosition.DIAGONAL else 0
                    result = self.apply_watermark_tile(image, wm, spacing, angle)
                else:
                    result = self.apply_watermark_position(image, wm, position, margin)
                
                # 转换回原来的模式（如果需要）
                if original_mode != 'RGBA':
                    if original_mode == 'RGB':
                        # 创建白色背景
                        background = Image.new('RGB', result.size, (255, 255, 255))
                        background.paste(result, mask=result.split()[-1])
                        result = background
                    else:
                        result = result.convert(original_mode)
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 保存结果
                # 获取原图的保存参数
                save_kwargs = {}
                if original_mode == 'JPEG' or output_path.lower().endswith(('.jpg', '.jpeg')):
                    save_kwargs['quality'] = 95
                    save_kwargs['optimize'] = True
                
                result.save(output_path, **save_kwargs)
                
                self.logger.info(f"处理完成: {input_path} -> {output_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"处理图片失败 {input_path}: {e}")
            return False
    
    def batch_process(
        self,
        input_path: str,
        output_dir: str,
        watermark: Union[str, Image.Image],
        recursive: bool = False,
        suffix: str = "_watermarked",
        **kwargs
    ) -> Tuple[int, int]:
        """批量处理图片"""
        # 获取所有图片文件
        image_files = self.get_image_files(input_path, recursive)
        
        if not image_files:
            self.logger.warning(f"在 {input_path} 中没有找到支持的图片文件")
            return 0, 0
        
        success_count = 0
        total_count = len(image_files)
        
        self.logger.info(f"开始批量处理 {total_count} 张图片...")
        
        # 使用进度条显示处理进度
        with tqdm(image_files, desc="处理进度", unit="张") as pbar:
            for image_file in pbar:
                try:
                    # 生成输出文件名
                    input_file = Path(image_file)
                    output_filename = f"{input_file.stem}{suffix}{input_file.suffix}"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # 处理单张图片
                    if self.process_single_image(image_file, output_path, watermark, **kwargs):
                        success_count += 1
                    
                    # 更新进度条描述
                    pbar.set_postfix({
                        '成功': success_count, 
                        '失败': total_count - success_count
                    })
                    
                except KeyboardInterrupt:
                    self.logger.info("用户中断处理")
                    break
                except Exception as e:
                    self.logger.error(f"处理文件 {image_file} 时出错: {e}")
        
        failed_count = total_count - success_count
        self.logger.info(f"批量处理完成: 成功 {success_count} 张，失败 {failed_count} 张")
        
        return success_count, failed_count 