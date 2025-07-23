#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from watermark_processor import WatermarkProcessor, WatermarkPosition
from pathlib import Path
import queue
import time

class WatermarkGUI:
    """图片水印工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ 图片批量水印工具 v1.0 - by Shiro")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置窗口图标
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        self.processor = WatermarkProcessor()
        self.processing = False
        self.log_queue = queue.Queue()
        
        # 变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.watermark_text = tk.StringVar()
        self.watermark_image_path = tk.StringVar()
        self.position = tk.StringVar(value="tile")
        self.opacity = tk.DoubleVar(value=0.5)
        self.size_ratio = tk.DoubleVar(value=0.2)
        self.rotation = tk.IntVar(value=45)
        self.spacing = tk.IntVar(value=50)
        self.margin = tk.IntVar(value=20)
        self.recursive = tk.BooleanVar(value=False)
        self.preview_mode = tk.BooleanVar(value=True)
        self.watermark_type = tk.StringVar(value="text")  # text 或 image
        
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 标题
        title_label = ttk.Label(main_frame, text="🖼️ 图片批量水印工具", 
                               font=("", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # 作者信息
        author_label = ttk.Label(main_frame, text="作者: Shiro", 
                                font=("", 10))
        author_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # 输入路径选择
        ttk.Label(main_frame, text="输入路径:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_input).grid(row=row, column=2, pady=5)
        row += 1
        
        # 输出路径选择
        ttk.Label(main_frame, text="输出目录:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_output).grid(row=row, column=2, pady=5)
        row += 1
        
        # 水印类型选择
        watermark_frame = ttk.LabelFrame(main_frame, text="水印设置", padding="10")
        watermark_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        watermark_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 水印类型单选按钮
        type_frame = ttk.Frame(watermark_frame)
        type_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(type_frame, text="文字水印", variable=self.watermark_type, 
                       value="text", command=self.on_watermark_type_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type, 
                       value="image", command=self.on_watermark_type_change).pack(side=tk.LEFT)
        
        # 文字水印输入
        self.text_frame = ttk.Frame(watermark_frame)
        self.text_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.text_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.text_frame, text="水印文字:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.text_frame, textvariable=self.watermark_text, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # 图片水印选择
        self.image_frame = ttk.Frame(watermark_frame)
        self.image_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.image_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.image_frame, text="水印图片:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.image_frame, textvariable=self.watermark_image_path, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(self.image_frame, text="选择", command=self.browse_watermark_image).grid(row=0, column=2)
        
        # 参数设置框架
        params_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="10")
        params_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        row += 1
        
        # 第一行参数
        ttk.Label(params_frame, text="水印位置:").grid(row=0, column=0, sticky=tk.W, pady=5)
        position_combo = ttk.Combobox(params_frame, textvariable=self.position, values=[
            "tile", "diagonal", "center", "top_left", "top_right", "bottom_left", "bottom_right"
        ], state="readonly", width=15)
        position_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 20))
        
        ttk.Label(params_frame, text="透明度:").grid(row=0, column=2, sticky=tk.W, pady=5)
        opacity_scale = ttk.Scale(params_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, 
                                 variable=self.opacity, length=150)
        opacity_scale.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.opacity_label = ttk.Label(params_frame, text="0.5")
        self.opacity_label.grid(row=0, column=4, sticky=tk.W, pady=5, padx=(5, 0))
        opacity_scale.configure(command=self.update_opacity_label)
        
        # 第二行参数
        ttk.Label(params_frame, text="大小比例:").grid(row=1, column=0, sticky=tk.W, pady=5)
        size_scale = ttk.Scale(params_frame, from_=0.05, to=1.0, orient=tk.HORIZONTAL, 
                              variable=self.size_ratio, length=150)
        size_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 20))
        self.size_label = ttk.Label(params_frame, text="0.2")
        self.size_label.grid(row=1, column=2, sticky=tk.W, pady=5)
        size_scale.configure(command=self.update_size_label)
        
        ttk.Label(params_frame, text="旋转角度:").grid(row=1, column=3, sticky=tk.W, pady=5, padx=(20, 0))
        rotation_spin = ttk.Spinbox(params_frame, from_=-180, to=180, textvariable=self.rotation, width=10)
        rotation_spin.grid(row=1, column=4, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 第三行参数
        ttk.Label(params_frame, text="水印间距:").grid(row=2, column=0, sticky=tk.W, pady=5)
        spacing_spin = ttk.Spinbox(params_frame, from_=0, to=200, textvariable=self.spacing, width=10)
        spacing_spin.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 20))
        
        ttk.Label(params_frame, text="边距:").grid(row=2, column=2, sticky=tk.W, pady=5)
        margin_spin = ttk.Spinbox(params_frame, from_=0, to=100, textvariable=self.margin, width=10)
        margin_spin.grid(row=2, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 选项设置
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="预览模式", variable=self.preview_mode).pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1
        
        self.start_button = ttk.Button(button_frame, text="🚀 开始处理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📋 支持格式", command=self.show_formats).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❓ 帮助", command=self.show_help).pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        row += 1
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始化界面状态
        self.on_watermark_type_change()
    
    def setup_logging(self):
        """设置日志记录"""
        # 重定向processor的日志到GUI
        import logging
        
        class GUILogHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
            
            def emit(self, record):
                self.log_queue.put(self.format(record))
        
        logger = logging.getLogger('WatermarkProcessor')
        gui_handler = GUILogHandler(self.log_queue)
        gui_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(gui_handler)
        
        # 定期检查日志队列
        self.check_log_queue()
    
    def check_log_queue(self):
        """检查日志队列并更新界面"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_message(message)
        except queue.Empty:
            pass
        
        # 每100ms检查一次
        self.root.after(100, self.check_log_queue)
    
    def log_message(self, message):
        """在日志区域显示消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_opacity_label(self, value):
        """更新透明度标签"""
        self.opacity_label.config(text=f"{float(value):.2f}")
    
    def update_size_label(self, value):
        """更新大小标签"""
        self.size_label.config(text=f"{float(value):.2f}")
    
    def on_watermark_type_change(self):
        """水印类型改变时的处理"""
        if self.watermark_type.get() == "text":
            # 显示文字输入，隐藏图片选择
            for widget in self.text_frame.winfo_children():
                widget.grid()
            for widget in self.image_frame.winfo_children():
                widget.grid_remove()
        else:
            # 显示图片选择，隐藏文字输入
            for widget in self.text_frame.winfo_children():
                widget.grid_remove()
            for widget in self.image_frame.winfo_children():
                widget.grid()
    
    def browse_input(self):
        """浏览输入路径"""
        path = filedialog.askdirectory(title="选择输入目录")
        if path:
            self.input_path.set(path)
    
    def browse_output(self):
        """浏览输出路径"""
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_path.set(path)
    
    def browse_watermark_image(self):
        """浏览水印图片"""
        file_types = [
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]
        path = filedialog.askopenfilename(title="选择水印图片", filetypes=file_types)
        if path:
            self.watermark_image_path.set(path)
    
    def validate_inputs(self):
        """验证输入参数"""
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入路径")
            return False
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("错误", "输入路径不存在")
            return False
        
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出目录")
            return False
        
        if self.watermark_type.get() == "text":
            if not self.watermark_text.get():
                messagebox.showerror("错误", "请输入水印文字")
                return False
        else:
            if not self.watermark_image_path.get():
                messagebox.showerror("错误", "请选择水印图片")
                return False
            if not os.path.exists(self.watermark_image_path.get()):
                messagebox.showerror("错误", "水印图片文件不存在")
                return False
        
        return True
    
    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return
        
        if self.processing:
            return
        
        # 创建输出目录
        try:
            os.makedirs(self.output_path.get(), exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建输出目录: {e}")
            return
        
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 在单独线程中处理
        self.processing_thread = threading.Thread(target=self.process_images)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """停止处理"""
        self.processing = False
        self.status_label.config(text="正在停止...")
    
    def process_images(self):
        """处理图片（在单独线程中运行）"""
        try:
            # 准备参数
            watermark = self.watermark_text.get() if self.watermark_type.get() == "text" else self.watermark_image_path.get()
            
            position_map = {
                'tile': WatermarkPosition.TILE,
                'diagonal': WatermarkPosition.DIAGONAL,
                'center': WatermarkPosition.CENTER,
                'top_left': WatermarkPosition.TOP_LEFT,
                'top_right': WatermarkPosition.TOP_RIGHT,
                'bottom_left': WatermarkPosition.BOTTOM_LEFT,
                'bottom_right': WatermarkPosition.BOTTOM_RIGHT,
            }
            
            kwargs = {
                'position': position_map[self.position.get()],
                'opacity': self.opacity.get(),
                'size_ratio': self.size_ratio.get(),
                'rotation': self.rotation.get(),
                'spacing': self.spacing.get(),
                'margin': self.margin.get(),
            }
            
            # 获取图片文件列表
            image_files = self.processor.get_image_files(self.input_path.get(), self.recursive.get())
            
            if self.preview_mode.get():
                image_files = image_files[:1]
            
            if not image_files:
                self.root.after(0, lambda: self.log_message("没有找到支持的图片文件"))
                return
            
            total_files = len(image_files)
            self.root.after(0, lambda: self.progress.config(maximum=total_files))
            self.root.after(0, lambda: self.status_label.config(text=f"开始处理 {total_files} 张图片..."))
            
            success_count = 0
            
            for i, image_file in enumerate(image_files):
                if not self.processing:
                    break
                
                try:
                    # 生成输出文件名
                    input_file = Path(image_file)
                    output_filename = f"{input_file.stem}_watermarked{input_file.suffix}"
                    output_path = os.path.join(self.output_path.get(), output_filename)
                    
                    # 处理单张图片
                    if self.processor.process_single_image(image_file, output_path, watermark, **kwargs):
                        success_count += 1
                    
                    # 更新进度
                    self.root.after(0, lambda: self.progress.config(value=i + 1))
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"处理中... {i + 1}/{total_files} (成功: {success_count})"
                    ))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"处理文件 {image_file} 时出错: {e}"))
            
            # 处理完成
            failed_count = len(image_files) - success_count
            if self.processing:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"处理完成！成功: {success_count}, 失败: {failed_count}"
                ))
                if success_count > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "完成", f"处理完成！\n成功: {success_count} 张\n失败: {failed_count} 张\n输出目录: {self.output_path.get()}"
                    ))
            else:
                self.root.after(0, lambda: self.status_label.config(text="处理已停止"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出错: {e}"))
        finally:
            self.processing = False
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
    
    def show_formats(self):
        """显示支持的格式"""
        formats_text = """支持的图片格式：

• JPEG (.jpg, .jpeg) - 最常用的图片格式
• PNG (.png) - 支持透明背景的格式
• BMP (.bmp) - Windows位图格式
• TIFF (.tiff, .tif) - 高质量图片格式
• WebP (.webp) - Google开发的现代格式
• GIF (.gif) - 动图格式（处理为静态图）

所有格式都支持批量处理！"""
        
        messagebox.showinfo("支持的格式", formats_text)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """🖼️ 图片批量水印工具使用帮助

1. 选择输入路径：
   • 可以选择包含图片的文件夹
   • 支持多种常见图片格式

2. 选择输出目录：
   • 处理后的图片将保存到此目录
   • 如果目录不存在会自动创建

3. 设置水印：
   • 文字水印：直接输入想要的文字
   • 图片水印：选择水印图片文件

4. 参数调整：
   • 位置：tile(平铺), center(居中), 各角落等
   • 透明度：0.1-1.0，数值越小越透明
   • 大小比例：相对于原图的大小比例
   • 旋转角度：-180到180度

5. 处理选项：
   • 递归处理：包含子目录中的图片
   • 预览模式：只处理第一张图片预览效果

使用技巧：
• 建议先用预览模式查看效果
• tile模式适合防盗版水印
• 调整透明度可以让水印更自然"""
        
        messagebox.showinfo("使用帮助", help_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = WatermarkGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("程序被用户中断")

if __name__ == "__main__":
    main() 